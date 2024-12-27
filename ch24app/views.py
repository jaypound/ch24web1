import logging
from django.shortcuts import render, redirect, get_object_or_404
from .models import Creator, Program, Episode, EpisodeMediaInfo
from .forms import CreatorForm, ProgramForm, EpisodeForm, EpisodeUploadForm, EpisodeUpdateForm
from django.http import HttpResponseRedirect, HttpResponse
from .utils import create_presigned_url, convert_seconds_to_timecode  # Assuming the function is in utils.py
from django.contrib import messages
from django.urls import reverse
import requests
import boto3
from pymediainfo import MediaInfo
from .utils import validate_media_info, create_presigned_view_url  # Import the validation function
from django.core.exceptions import ValidationError

import os
from django.conf import settings

AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

# from .models import MediaInfo

# logger = logging.getLogger('django')
# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    user_has_creator = False
    user_has_programs = False
    if request.user.is_authenticated:
        user_has_creator = Creator.objects.filter(created_by=request.user).exists() 
        user_has_programs = Program.objects.filter(created_by=request.user).exists()
        print(f"user_has_creator: {user_has_creator}")
        print(f"user_has_programs: {user_has_programs}")

    return render(request, 'home.html', {'user_has_creator': user_has_creator, 'user_has_programs': user_has_programs})

def all_creators(request):
    creator_list = Creator.objects.all()
    return render(request, 'creator_list.html', {'creator_list': creator_list})

def all_programs(request):
    program_list = Program.objects.all()
    return render(request, 'program_list.html', {'program_list': program_list})

def all_episodes(request):
    episode_list = Episode.objects.all()
    return render(request, 'episode_list.html', {'episode_list': episode_list})

def my_creators(request):
    creator_list = Creator.objects.filter(created_by=request.user)
    return render(request, 'my_creators.html', {'creator_list': creator_list})

def my_programs(request):
    program_list = Program.objects.filter(created_by=request.user)
    return render(request, 'my_programs.html', {'program_list': program_list})

# def my_episodes(request):
#     episode_list = Episode.objects.filter(created_by=request.user)
#     return render(request, 'my_episodes.html', {'episode_list': episode_list})

def my_episodes(request):
    episode_list = Episode.objects.filter(created_by=request.user)
    return render(request, 'my_episodes.html', {'episode_list': episode_list})


# def my_episodes(request):
#     episode_list = Episode.objects.filter(created_by=request.user).prefetch_related('media_infos')
    
#     # Prepare a list of episodes with their MediaInfo error status
#     for episode in episode_list:
#         media_infos = episode.media_infos.all()
#         unique_errors, unique_warnings = validate_media_info(media_infos)
#         mediainfo_errors = bool(unique_errors)
#         # Attach the error status to the episode object
#         episode.mediainfo_errors = mediainfo_errors
    
#     return render(request, 'my_episodes.html', {'episode_list': episode_list})


def add_creator(request):
    submitted = False
    form = CreatorForm()
    if request.method == 'POST':
        form = CreatorForm(request.POST, user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)  # Create an instance without saving to the database
            instance.created_by = request.user  # Set the created_by field to the current user
            instance.save()  # Now save the instance to the database
            return HttpResponseRedirect('/add_creator?submitted=True')
    else:
        form = CreatorForm(user=request.user)
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_creator.html', {'form': form, 'submitted': submitted})


# from django.shortcuts import render, HttpResponseRedirect
# from .forms import ProgramForm

# views.py

from django.shortcuts import render, HttpResponseRedirect
from .forms import ProgramForm
from .models import Creator

# def add_program(request):
#     submitted = False
#     if request.method == 'POST':
#         form = ProgramForm(request.POST)
#         if form.is_valid():
#             instance = form.save(commit=False)
#             instance.created_by = request.user  # Set the created_by field

#             # Set the creator field to the last creator associated with the user
#             creators = Creator.objects.filter(created_by=request.user)
#             if creators.exists():
#                 instance.creator = creators.last()
#             else:
#                 # Handle the case where the user has no creators
#                 # You might want to redirect or display an error message
#                 return HttpResponseRedirect('/no_creator_found')

#             instance.save()
#             return HttpResponseRedirect('/add_program?submitted=True')
#     else:
#         form = ProgramForm()
#         if 'submitted' in request.GET:
#             submitted = True
#     return render(request, 'add_program.html', {'form': form, 'submitted': submitted})

from django.urls import reverse

def add_program(request):
    submitted = False
    if request.method == 'POST':
        form = ProgramForm(request.POST, user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            return HttpResponseRedirect(f'{reverse("add-program")}?submitted=True')
    else:
        initial_data = {}
        last_creator = Creator.objects.filter(created_by=request.user).order_by('-created_at').first()
        if not last_creator:
            messages.error(request, "You need to add a Channel before adding programs.")
            creator_form = CreatorForm(user=request.user)
            submitted = False
            return render(request, 'add_creator.html', {'form': creator_form, 'submitted': submitted})        

        if last_creator:
            initial_data['creator'] = last_creator  # Pre-fill the 'program' field

        form = ProgramForm(user=request.user, initial=initial_data)
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_program.html', {'form': form, 'submitted': submitted})


def no_creator_found(request):
    return render(request, 'no_creator_found.html')


def add_episode(request):
    if request.method == 'POST':
        form = EpisodeForm(request.POST, user=request.user)
        if form.is_valid():
            episode = form.save(commit=False)
            episode.created_by = request.user
            episode.save()
            # Redirect with episode_id in query parameters
            return HttpResponseRedirect(f'{reverse("add-episode")}?submitted=True&episode_id={episode.custom_id}')
    else:
        # Prepare initial data for the form
        initial_data = {}
        last_program = Program.objects.filter(created_by=request.user).order_by('-created_at').first()
        if not last_program:
            messages.error(request, "You need to add a program before adding episodes.")
            program_form = ProgramForm(user=request.user)
            return render(request, 'add_program.html', {'form': program_form, 'submitted': False})        

        if last_program:
            initial_data['program'] = last_program  # Pre-fill the 'program' field

        form = EpisodeForm(user=request.user, initial=initial_data)
    
    submitted = 'submitted' in request.GET
    episode = None
    if submitted and 'episode_id' in request.GET:
        episode_id = request.GET.get('episode_id')
        episode = get_object_or_404(Episode, custom_id=episode_id)
    
    return render(request, 'add_episode.html', {'form': form, 'submitted': submitted, 'episode': episode})

# views.py

from django.shortcuts import render, get_object_or_404
from .models import Episode
from .forms import EpisodeAnalysisForm

def episode_analysis_view(request, custom_id):
    """
    View to display the analysis of a specific episode in read-only mode.
    """
    # Fetch the Episode instance based on the custom_id
    episode = get_object_or_404(Episode, custom_id=custom_id)
    
    # Instantiate the form with the Episode instance
    form = EpisodeAnalysisForm(instance=episode)
    
    context = {
        'form': form,
        'episode': episode,  # Optional: Pass the episode object if needed in the template
    }
    
    return render(request, 'my_episode_analysis.html', context)


def update_creator(request, creator_id):
    creator = Creator.objects.get(custom_id=creator_id)  # Changed from id to custom_id
    if request.method == "POST":
        form = CreatorForm(request.POST, instance=creator)
        if form.is_valid():
            form.save()
            return render(request, 'update_creator.html', {
                'form': form,
                'submitted': True
            })
    else:
        form = CreatorForm(instance=creator)
    
    return render(request, 'update_creator.html', {
        'form': form,
        'submitted': False
    })

# views.py

from django.urls import reverse
from django.http import HttpResponseRedirect

def update_program(request, program_id):
    program = Program.objects.get(pk=program_id)
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f'{reverse("update-program", args=[program_id])}?submitted=True')
    else:
        form = ProgramForm(instance=program, user=request.user)
    return render(request, 'update_program.html', {'form': form, 'submitted': request.GET.get('submitted', False)})


# def update_program(request, program_id):
#     program = Program.objects.get(pk=program_id)
#     if request.method == 'POST':
#         form = ProgramForm(request.POST, instance=program)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(f'{reverse("update-program", args=[program_id])}?submitted=True')
#     else:
#         form = ProgramForm(instance=program)
#     return render(request, 'update_program.html', {'form': form, 'submitted': request.GET.get('submitted', False)})


def update_episode(request, episode_id):
    episode = Episode.objects.get(custom_id=episode_id)  # Changed from id to custom_id
    if request.method == "POST":
        form = EpisodeUpdateForm(request.POST, instance=episode)
        if form.is_valid():
            form.save()
            return render(request, 'update_episode.html', {
                'form': form,
                'submitted': True
            })
    else:
        form = EpisodeUpdateForm(instance=episode)
    
    return render(request, 'update_episode.html', {
        'form': form,
        'submitted': False
    })

def get_mediainfo_from_s3(bucket_name, s3_key):
    # Initialize a session using Amazon S3
    s3 = boto3.client('s3')

    # Define a temporary file path
    temp_file_path = os.path.join(settings.MEDIA_ROOT, '', os.path.basename(s3_key))

    print('Temp file path: ', temp_file_path)
    logger.info(f'Temp file path: {temp_file_path}')

    # Download the file from S3
    s3.download_file(bucket_name, s3_key, temp_file_path)

    # Use pymediainfo to get media information
    media_info = MediaInfo.parse(temp_file_path)
    # pprint(media_info)

    # Clean up the temporary file
    os.remove(temp_file_path)

    return media_info


# views.py

from .utils import validate_media_info  # Ensure this is imported

import boto3
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

from .forms import EpisodeUploadForm
from .models import Episode, EpisodeMediaInfo
# from .mediainfo_utils import get_mediainfo_from_s3, validate_media_info

AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)

def upload_episode(request, episode_id):
    episode = get_object_or_404(Episode, custom_id=episode_id)

    # Security check: Ensure the user is the creator of the episode
    if episode.created_by != request.user:
        return HttpResponse("Unauthorized", status=401)

    if request.method == 'POST':
        form = EpisodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Delete previous EpisodeMediaInfo instances
            EpisodeMediaInfo.objects.filter(episode=episode).delete()

            file = form.cleaned_data['file']
            file_name = file.name

            bucket_name = AWS_STORAGE_BUCKET_NAME
            unique_file_name = f'{episode.custom_id}/{file_name}'

            # Initialize the S3 client
            s3_client = boto3.client('s3')

            # Upload the file to S3
            try:
                with file.open('rb') as f:
                    s3_client.upload_fileobj(f, bucket_name, unique_file_name)
            except Exception as e:
                messages.error(request, f"Upload failed: {e}")
                return redirect('upload_failed')

            # If we reach here, the upload was successful.
            # Get media info from the uploaded file
            media_info = get_mediainfo_from_s3(bucket_name, unique_file_name)

            # Save media info to the database
            track_id = 0
            for track in media_info.tracks:
                track_id += 1
                track_metadata = {
                    key: value for key, value in track.to_data().items() if value is not None
                }

                EpisodeMediaInfo.objects.create(
                    episode=episode,
                    track_id=track_id,
                    metadata=track_metadata
                )

            # Retrieve the saved media_infos
            media_infos = episode.media_infos.all()

            # Use the validation function
            unique_errors, unique_warnings = validate_media_info(media_infos)

            # Set the has_mediainfo_errors field based on validation
            episode.has_mediainfo_errors = bool(unique_errors)

            # Update the episode with the file name
            episode.file_name = unique_file_name
            episode.save()

            messages.success(request, "File uploaded successfully.")

            # At the end of upload_episode, after media_info is created:
            try:
                media_info_track1 = EpisodeMediaInfo.objects.get(episode=episode, track_id=1)
                duration_ms = media_info_track1.metadata.get('duration')

                if duration_ms:
                    # Convert to seconds
                    duration_sec = float(duration_ms) / 1000
                    
                    # Populate the episode fields
                    episode.duration_seconds = duration_sec
                    episode.duration_timecode = convert_seconds_to_timecode(duration_sec)
                    episode.save()
            except EpisodeMediaInfo.DoesNotExist:
                pass  # Handle the case where track_id=1 doesn't exist

            # Redirect without the mediainfo_errors flag
            return redirect(f"{reverse('upload_success')}?episode_id={episode.custom_id}")
        
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = EpisodeUploadForm()

    return render(request, 'episode_upload.html', {'form': form, 'episode': episode})




def upload_success(request):
    episode_id = request.GET.get('episode_id')
    episode = get_object_or_404(Episode, custom_id=episode_id) if episode_id else None

    return render(request, 'upload_success.html', {
        'episode': episode,
    })



def upload_failed(request):
    return render(request, 'upload_failed.html')

def adobe_premiere(request):
    return render(request, 'adobe_premiere.html')

def davinci_resolve(request):
    return render(request, 'davinci_resolve.html')

# def getting_started2(request):
#     return render(request, 'getting_started2.html')

def getting_started(request):
    return render(request, 'getting_started.html')

def episode_media_info(request, episode_id):
    episode = get_object_or_404(Episode, custom_id=episode_id)
    media_infos = episode.media_infos.all()

    # Use the validation function
    unique_errors, unique_warnings = validate_media_info(media_infos)

    # Update the has_mediainfo_errors field
    episode.has_mediainfo_errors = bool(unique_errors)
    episode.save()

    # Add unique error messages to the Django messages framework as errors
    for message in unique_errors:
        messages.error(request, message)

    # Add unique warning messages to the Django messages framework as warnings
    for message in unique_warnings:
        messages.warning(request, message)

    return render(request, 'episode_media_info.html', {
            'episode': episode,
            'media_infos': media_infos,
            'errors': unique_errors,
            'warnings': unique_warnings
        })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .forms import SupportTicketForm, SupportTicketStatusForm, TicketResponseForm
from .models import SupportTicket, TicketResponse

def submit_ticket(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            if request.user.is_authenticated:
                creator = Creator.objects.filter(created_by=request.user).first()
                if creator:
                    ticket.creator = creator
                ticket.created_by = request.user  # Assign 'created_by'
                print(f"request.user: {request.user}")  # Debugging statement
                print(f"ticket.created_by: {ticket.created_by}")  # Debugging statement
            else:
                print("User is not authenticated.")
            ticket.save()
            return redirect('ticket_submitted', ticket_no=ticket.ticket_no)
    else:
        form = SupportTicketForm(user=request.user)
    return render(request, 'support/submit_ticket.html', {'form': form})


def ticket_submitted(request, ticket_no):
    ticket = get_object_or_404(SupportTicket, ticket_no=ticket_no)
    return render(request, 'support/ticket_submitted.html', {'ticket': ticket})

def ticket_detail(request, ticket_no):
    ticket = get_object_or_404(SupportTicket, ticket_no=ticket_no)
    responses = ticket.responses.all().order_by('response_no')
    status_form = None
    response_form = TicketResponseForm()

    if request.method == 'POST':
        if 'status_form' in request.POST and request.user.is_staff:
            status_form = SupportTicketStatusForm(request.POST, instance=ticket)
            if status_form.is_valid():
                status_form.save()
                return redirect('ticket_detail', ticket_no=ticket_no)
        elif 'response_form' in request.POST:
            response_form = TicketResponseForm(request.POST)
            if response_form.is_valid():
                response = response_form.save(commit=False)
                response.ticket = ticket
                if request.user.is_authenticated:
                    response.responder = request.user
                response.save()
                return redirect('ticket_detail', ticket_no=ticket_no)
    else:
        if request.user.is_staff:
            status_form = SupportTicketStatusForm(instance=ticket)

    return render(request, 'support/ticket_detail.html', {
        'ticket': ticket,
        'responses': responses,
        'response_form': response_form,
        'status_form': status_form,
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SupportTicket

@login_required
def my_tickets(request):
    tickets = SupportTicket.objects.filter(created_by=request.user).order_by('-time_received')
    return render(request, 'support/my_tickets.html', {'tickets': tickets})


def view_episode(request, episode_id):
    episode = get_object_or_404(Episode, custom_id=episode_id)

    # Security check: Ensure the user is allowed to view the episode
    if episode.created_by != request.user:
        return HttpResponse("Unauthorized", status=401)

    bucket_name = AWS_STORAGE_BUCKET_NAME
    s3_key = episode.file_name

    # Generate pre-signed URL
    presigned_url = create_presigned_view_url(bucket_name, s3_key)

    if presigned_url:
        # Pass the URL to the template
        return render(request, 'view_episode.html', {
            'episode': episode,
            'presigned_url': presigned_url,
        })
    else:
        messages.error(request, "Unable to generate view URL.")
        return redirect('error_page')  # Replace with your actual error page


from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK", status=200)

import os
from django.http import JsonResponse

def environment(request):
    """
    View to display all environment variables.
    """
    excluded_keywords = ["DATABASE", "DJANGO", "AWS", "PYENV", "HOME", "USER", "PATH", "LOGNAME", "PWD", "VIRTUAL_ENV", "ZDOTDIR"]  # Keywords to exclude
    env_vars = {
        key: value
        for key, value in os.environ.items()
        if not any(keyword in key for keyword in excluded_keywords)
    }
    return render(request, 'environment_variables.html', {'env_vars': env_vars})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime
from .utils import schedule_episodes
from django.utils import timezone
from .models import Episode, ScheduledEpisode
import csv
import io
import pytz

# @login_required
# @user_passes_test(lambda u: u.is_staff)  # Ensures only admin users can access
# def playlist_create(request):
#     if request.method == 'POST':
#         action = request.POST.get('action')
#         playlist_date = request.POST.get('playlist_date')
        
#         if not playlist_date:
#             messages.error(request, 'Please select a date')
#             return render(request, 'playlist_create.html')
            
#         try:
#             date_obj = datetime.strptime(playlist_date, '%Y-%m-%d').date()
            
#             if action == 'create':
#                 # Call your scheduling function
#                 schedule_episodes(date_obj, all_ready=True)
#                 messages.success(request, f'Playlist created for {playlist_date}')
                
#             elif action == 'clear':
#                 # Clear existing schedule for the date
#                 ScheduledEpisode.objects.filter(schedule_date=date_obj).delete()
#                 messages.success(request, f'Schedule cleared for {playlist_date}')
                
#             elif action == 'export':
#                 # Generate CSV export
#                 return export_playlist(date_obj)
                
#         except Exception as e:
#             messages.error(request, f'Error: {str(e)}')
            
#     return render(request, 'playlist_create.html')

# def export_playlist(date_obj):
#     """Export playlist to CSV file"""
#     buffer = io.StringIO()
#     writer = csv.writer(buffer)
#     user_timezone = pytz.timezone(settings.TIME_ZONE)
    
#     # Write header
#     writer.writerow([
#         'Start Time', 'End Time', 'Title', 'Duration', 
#         'Rating', 'Genre', 'Creator'
#     ])
    
#     # Get scheduled episodes for the date
#     schedule = ScheduledEpisode.objects.filter(
#         schedule_date=date_obj
#     ).order_by('start_time')
    
#     # Write data rows
#     for episode in schedule:
#         local_start = timezone.localtime(
#             timezone.make_aware(datetime.combine(date_obj, episode.start_time)),
#             timezone=user_timezone
#         )
#         local_end = timezone.localtime(
#             timezone.make_aware(datetime.combine(date_obj, episode.end_time)),
#             timezone=user_timezone
#         )

#         writer.writerow([
#             episode.start_time.strftime('%H:%M:%S'),
#             episode.end_time.strftime('%H:%M:%S'),
#             episode.title,
#             episode.duration_timecode,
#             episode.ai_age_rating,
#             episode.ai_genre,
#             episode.creator.channel_name
#         ])
    
#     # Create response
#     buffer.seek(0)
#     response = HttpResponse(buffer, content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="playlist_{date_obj}.csv"'
    
#     return response

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.contrib import messages
from datetime import datetime
import pytz

@login_required
@user_passes_test(lambda u: u.is_staff)
def playlist_create(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        playlist_date_str = request.POST.get('playlist_date')
        
        if not playlist_date_str:
            messages.error(request, 'Please select a date')
            return render(request, 'playlist_create.html')
            
        try:
            playlist_date = datetime.strptime(playlist_date_str, '%Y-%m-%d').date()
            
            if action == 'create':
                # Check if schedule already exists
                existing_schedule = ScheduledEpisode.objects.filter(schedule_date=playlist_date).exists()
                if existing_schedule:
                    messages.warning(request, f'Schedule already exists for {playlist_date}. Clear it first.')
                else:
                    schedule_episodes(playlist_date, all_ready=True)
                    messages.success(request, f'Playlist created for {playlist_date}')
                
            elif action == 'clear':
                deleted_count = ScheduledEpisode.objects.filter(schedule_date=playlist_date).delete()[0]
                messages.success(request, f'Cleared {deleted_count} scheduled episodes for {playlist_date}')
                
            elif action == 'export':
                return export_playlist(playlist_date)
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Get today's schedule for display
    today = timezone.now().date()
    scheduled_episodes = ScheduledEpisode.objects.filter(
        schedule_date=today
    ).select_related('episode', 'program', 'creator').order_by('start_time')
    
    context = {
        'scheduled_episodes': scheduled_episodes,
        'selected_date': request.POST.get('playlist_date', today.strftime('%Y-%m-%d'))
    }
    
    return render(request, 'playlist_create.html', context)

# def export_playlist(schedule_date):
#     """Export playlist to CSV file"""
#     buffer = io.StringIO()
#     writer = csv.writer(buffer)
#     user_timezone = pytz.timezone(settings.TIME_ZONE)
    
#     writer.writerow([
#         'Schedule Date',
#         'Start Time (UTC)',
#         'Start Time (Local)',
#         'Title',
#         'Duration',
#         'Rating',
#         'Genre',
#         'Creator'
#     ])
    
#     schedule = ScheduledEpisode.objects.filter(
#         schedule_date=schedule_date
#     ).order_by('start_time')
    
#     for episode in schedule:
#         utc_start = timezone.make_aware(
#             datetime.combine(schedule_date, episode.start_time)
#         )
#         local_start = timezone.localtime(utc_start, timezone=user_timezone)
        
#         writer.writerow([
#             schedule_date.strftime('%Y-%m-%d'),
#             episode.start_time.strftime('%H:%M:%S'),
#             local_start.strftime('%H:%M:%S'),
#             episode.title,
#             episode.duration_timecode,
#             episode.ai_age_rating,
#             episode.ai_genre,
#             episode.creator.channel_name
#         ])
    
#     buffer.seek(0)
#     response = HttpResponse(buffer, content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="playlist_{schedule_date}.csv"'
    
#     return response

# def export_playlist(schedule_date):
#     """Export playlist with correct timezone handling"""
#     buffer = io.StringIO()
#     writer = csv.writer(buffer)
    
#     # Get timezone objects
#     utc = pytz.UTC
#     local_tz = pytz.timezone('America/New_York')  # Or get from settings
    
#     writer.writerow([
#         'Schedule Date',
#         'Start Time (UTC)',
#         'Start Time (Local)',
#         'Title',
#         'Duration',
#         'Rating',
#         'Genre',
#         'Creator'
#     ])
    
#     schedule = ScheduledEpisode.objects.filter(
#         schedule_date=schedule_date
#     ).order_by('start_time')
    
#     for episode in schedule:
#         # Create UTC datetime
#         utc_datetime = episode.start_time.astimezone(utc)
#         # Convert to local time
#         local_datetime = utc_datetime.astimezone(local_tz)
        
#         writer.writerow([
#             schedule_date.strftime('%Y-%m-%d'),
#             utc_datetime.strftime('%H:%M:%S'),
#             local_datetime.strftime('%H:%M:%S'),
#             episode.title,
#             episode.duration_timecode,
#             episode.ai_age_rating,
#             episode.ai_genre,
#             episode.creator.channel_name
#         ])

#     buffer.seek(0)
#     response = HttpResponse(buffer, content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="playlist_{schedule_date}.csv"'
    
#     return response

def export_playlist(schedule_date):
    """Export playlist with correct timezone handling"""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    
    utc = pytz.UTC
    local_tz = pytz.timezone('America/New_York')

    writer.writerow([
        'Schedule Date',
        'Start Time (UTC)',
        'Start Time (Local)',
        'Title',
        'Duration',
        'Rating',
        'Genre',
        'Creator'
    ])
    
    schedule = ScheduledEpisode.objects.filter(
        schedule_date=schedule_date
    ).order_by('start_time')
    
    for episode in schedule:
        # episode.start_time is already a datetime, so just convert:
        utc_datetime = episode.start_time.astimezone(utc)
        local_datetime = utc_datetime.astimezone(local_tz)
        
        writer.writerow([
            schedule_date.strftime('%Y-%m-%d'),
            utc_datetime.strftime('%H:%M:%S'),
            local_datetime.strftime('%H:%M:%S'),
            episode.title,
            episode.duration_timecode,
            episode.ai_age_rating,
            episode.ai_genre,
            episode.creator.channel_name
        ])

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="playlist_{schedule_date}.csv"'
    return response


# views.py
from django.shortcuts import render, redirect
from .forms import ScheduledEpisodeForm
from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.is_staff)
def scheduled_episode_create(request):
    if request.method == 'POST':
        form = ScheduledEpisodeForm(request.POST)
        if form.is_valid():
            try:
                scheduled_episode = form.save()
                messages.success(request, 'Episode scheduled successfully')
                return redirect('scheduled_episode_detail', pk=scheduled_episode.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ScheduledEpisodeForm()
    
    return render(request, 'scheduled_episode_form.html', {'form': form})

# views.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from .models import Episode, GENRE_CHOICES, AGE_RATING_CHOICES, Creator

class AvailableContentView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Episode
    template_name = 'available_content.html'
    context_object_name = 'episodes'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = Episode.objects.filter(ready_for_air=True)
        
        # Apply filters from GET parameters
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(ai_genre=genre)
            
        age_rating = self.request.GET.get('age_rating')
        if age_rating:
            queryset = queryset.filter(ai_age_rating=age_rating)
            
        creator = self.request.GET.get('creator')
        if creator:
            queryset = queryset.filter(program__creator=creator)
            
        duration = self.request.GET.get('duration')
        if duration:
            if duration == 'bumper':
                queryset = queryset.filter(duration_seconds__lte=15)
            elif duration == 'shortform':
                queryset = queryset.filter(duration_seconds__gt=15, duration_seconds__lte=900)
            elif duration == 'longform':
                queryset = queryset.filter(duration_seconds__gt=900)

        # Apply search if provided
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(program__program_name__icontains=search) |
                Q(program__creator__channel_name__icontains=search)
            )

        # Apply sorting
        sort = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort)
        
        return queryset.select_related('program', 'program__creator')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filters'] = {
            'genre': self.request.GET.get('genre', ''),
            'age_rating': self.request.GET.get('age_rating', ''),
            'creator': self.request.GET.get('creator', ''),
            'duration': self.request.GET.get('duration', ''),
            'search': self.request.GET.get('search', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        context['genres'] = dict(GENRE_CHOICES)
        context['age_ratings'] = dict(AGE_RATING_CHOICES)
        context['creators'] = Creator.objects.all()
        context['duration_choices'] = [
            ('bumper', 'Bumper (≤15s)'),
            ('shortform', 'Short Form (15s-15m)'),
            ('longform', 'Long Form (>15m)'),
        ]
        return context