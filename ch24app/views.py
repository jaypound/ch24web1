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
from .models import HomeMessage

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

    active_message = HomeMessage.objects.filter(is_active=True).first()

    return render(request, 'home.html', {
        'user_has_creator': user_has_creator, 
        'user_has_programs': user_has_programs,
        'active_message': active_message
    })

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

# def my_programs(request):
#     program_list = Program.objects.filter(created_by=request.user)
#     return render(request, 'my_programs.html', {'program_list': program_list})

# from django.db.models import Count
from django.db import models

def my_programs(request):
    # Get all programs for the user
    program_list = Program.objects.filter(created_by=request.user)
    
    # For each program, annotate with episode count
    program_list = program_list.annotate(
        episode_count=models.Count('episode')
    )
    
    return render(request, 'my_programs.html', {'program_list': program_list})

def my_episodes(request):
    episode_list = Episode.objects.filter(created_by=request.user)
    return render(request, 'my_episodes.html', {'episode_list': episode_list})


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


# views.py

from django.shortcuts import render, HttpResponseRedirect
from .forms import ProgramForm
from .models import Creator


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

from django.shortcuts import render, get_object_or_404
from .models import Episode, TIME_SLOTS_CHOICES
# from .utils import TIME_SLOTS
from .forms import EpisodeAnalysisForm

from django.shortcuts import render, get_object_or_404
from .forms import EpisodeAnalysisForm
from .models import Episode

def update_analysis(request, custom_id):
    episode = get_object_or_404(Episode, custom_id=custom_id)

    if request.method == "POST":
        form = EpisodeAnalysisForm(request.POST, instance=episode)
        if form.is_valid():
            print("Form is valid!")
            form.save()
            return render(request, 'update_analysis.html', {'form': form, 'submitted': True})
        else:
            print(form.errors)

    else:
        form = EpisodeAnalysisForm(instance=episode)

    return render(request, 'update_analysis.html', {'form': form, 'submitted': False})


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

def sanitize_filename(filename):
    """
    Remove all characters outside of ASCII range.
    You can make this more selective as needed
    (e.g., only remove specific emoji ranges).
    """
    # Encode to ASCII and ignore errors, then decode back to str
    return filename.encode('ascii', errors='ignore').decode()

def verify_s3_object(bucket_name, object_key):
    """
    Check if an object with the specified key exists in S3.
    Returns True if it exists, False otherwise.
    """
    s3_client = boto3.client('s3')
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except Exception:
        return False

def upload_episode(request, episode_id):
    episode = get_object_or_404(Episode, custom_id=episode_id)

    # Security check
    if episode.created_by != request.user:
        return HttpResponse("Unauthorized", status=401)

    if request.method == 'POST':
        form = EpisodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Delete previous EpisodeMediaInfo instances
            EpisodeMediaInfo.objects.filter(episode=episode).delete()

            # Original filename from the uploaded file
            file = form.cleaned_data['file']
            original_file_name = file.name

            # Sanitize filename to remove emojis/unwanted unicode
            sanitized_file_name = sanitize_filename(original_file_name)

            # Construct S3 path: e.g. "episode123/myfile.mp4"
            bucket_name = AWS_STORAGE_BUCKET_NAME
            unique_file_name = f'{episode.custom_id}/{sanitized_file_name}'

            # Initialize the S3 client
            s3_client = boto3.client('s3')

            # Upload the file to S3
            try:
                with file.open('rb') as f:
                    s3_client.upload_fileobj(f, bucket_name, unique_file_name)
            except Exception as e:
                messages.error(request, f"Upload failed: {e}")
                return redirect('upload_failed')

            # Verify the object is actually in S3 after upload
            if not verify_s3_object(bucket_name, unique_file_name):
                messages.error(request, 
                    f"Upload failed: Could not verify '{unique_file_name}' in S3.")
                return redirect('upload_failed')

            # Optional message if sanitization changed the file name
            if original_file_name != sanitized_file_name:
                messages.info(
                    request,
                    f"Filename changed from '{original_file_name}' "
                    f"to '{sanitized_file_name}' to remove invalid characters."
                )

            # Retrieve the media info from the uploaded file
            media_info = get_mediainfo_from_s3(bucket_name, unique_file_name)

            # Save the media info to the database
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

            # Validate media info
            media_infos = episode.media_infos.all()
            unique_errors, unique_warnings = validate_media_info(media_infos)
            episode.has_mediainfo_errors = bool(unique_errors)

            # IMPORTANT: store the sanitized file name in the DB
            episode.file_name = unique_file_name
            episode.save()

            # Attempt to populate episode duration fields
            try:
                media_info_track1 = EpisodeMediaInfo.objects.get(episode=episode, track_id=1)
                duration_ms = media_info_track1.metadata.get('duration')
                if duration_ms:
                    duration_sec = float(duration_ms) / 1000
                    episode.duration_seconds = duration_sec
                    episode.duration_timecode = convert_seconds_to_timecode(duration_sec)
                    episode.save()
            except EpisodeMediaInfo.DoesNotExist:
                pass

            messages.success(request, "File uploaded successfully.")
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

@login_required
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

@login_required
def view_episode(request, episode_id):
    episode = get_object_or_404(Episode, custom_id=episode_id)

    # Security check: Ensure the user is allowed to view the episode
    # if episode.created_by != request.user:
    #     return HttpResponse("Unauthorized", status=401)

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
        return redirect('available_content')  # Replace with your actual error page


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
    logger.debug("Entered playlist_create view. Request method: %s", request.method)

    if request.method == 'POST':
        action = request.POST.get('action', '')
        playlist_date_str = request.POST.get('playlist_date', '')

        # Log the form submission details
        logger.debug("Form POST data -> action: '%s', playlist_date: '%s'", action, playlist_date_str)

        if not playlist_date_str:
            messages.error(request, 'Please select a date')
            logger.debug("No date provided in POST. Returning with error message.")
            return render(request, 'playlist_create.html')

        try:
            playlist_date = datetime.strptime(playlist_date_str, '%Y-%m-%d').date()
            logger.debug("Parsed playlist_date as: %s", playlist_date)

            if action == 'create':
                logger.debug("Checking if schedule already exists for %s", playlist_date)
                existing_schedule = ScheduledEpisode.objects.filter(schedule_date=playlist_date).exists()
                logger.debug("existing_schedule = %s", existing_schedule)

                if existing_schedule:
                    messages.warning(request, f'Schedule already exists for {playlist_date}. Clear it first.')
                    logger.debug("Schedule already exists. Skipping creation.")
                else:
                    logger.debug("Calling schedule_episodes() for date %s", playlist_date)
                    schedule_episodes(playlist_date, all_ready=True)
                    messages.success(request, f'Playlist created for {playlist_date}')

            elif action == 'clear':
                logger.debug("Clearing all scheduled episodes for date %s. (Currently clearing ALL, per your code.)", playlist_date)
                deleted_count = ScheduledEpisode.objects.all().delete()[0]
                messages.success(request, f'Cleared ALL {deleted_count} scheduled episodes!')
                logger.debug("Deleted %s scheduled episodes (all dates).", deleted_count)

            elif action == 'export':
                logger.debug("Exporting playlist for %s", playlist_date)
                return export_playlist(playlist_date)

            else:
                # If the action isn't recognized, it's probably just the date auto-submit
                logger.debug("No recognized action. Possibly the form auto-submitted on date change.")

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            logger.exception("An error occurred in playlist_create view.")

    # Instead of always using 'today', parse the selected date from POST or GET.
    selected_date_str = request.POST.get('playlist_date') or request.GET.get('playlist_date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            # Fallback if parsing fails
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    # Query the schedule using the selected date
    scheduled_episodes = ScheduledEpisode.objects.filter(
        schedule_date=selected_date
    ).select_related('episode', 'program', 'creator').order_by('start_time')

    context = {
        'scheduled_episodes': scheduled_episodes,
        'selected_date': selected_date.strftime('%Y-%m-%d'),
    }

    logger.debug(
        "Rendering playlist_create.html with %s scheduled episodes for date: %s",
        scheduled_episodes.count(),
        selected_date
    )

    return render(request, 'playlist_create.html', context)


from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime
import io
import pytz
import csv

# @login_required
# @user_passes_test(lambda u: u.is_staff)
def export_playlist(schedule_date):
    """
    Export a .ply playlist with lines like:
    "Z:\4bf15aac-059a-4de5-b17f-557703ace10a\ID1_2997_10Mbps.mp4";0.00000;41.07400;;ID1_2997_10Mbps
    """

    # If schedule_date is a string like "2025-01-08", parse it
    if isinstance(schedule_date, str):
        schedule_date = datetime.strptime(schedule_date, '%Y-%m-%d').date()

    # Prepare StringIO as our in-memory text buffer
    buffer = io.StringIO()

    # Query all ScheduledEpisode for the given date
    schedule = ScheduledEpisode.objects.filter(
        schedule_date=schedule_date
    ).order_by('start_time')

    # Write each line according to your requested format
    # Example line:
    # "Z:\{episode.custom_id}\{episode.file_name}";0.00000;{duration};;{title}
    for episode in schedule:
        # Build the file path in quotes
        # file_path = f"\"Z:\\{episode.custom_id}\\{episode.file_name}\""
        file_path = f"\"Z:\\{episode.file_name}\"".replace('/', '\\')

        # Start time is always 0.00000 in your example
        start_str = "0.00000"

        # Format duration with five decimals.
        # If duration_seconds is None, default to zero
        duration_value = float(episode.duration_seconds or 0)
        duration_str = f"{duration_value:.5f}"

        # Title (no quotes in your sample, just appended)
        title_str = episode.title

        # Construct the line
        line = f"{file_path};{start_str};{duration_str};;{title_str}"

        # Write the line plus a newline
        buffer.write(line + "\n")

    # Reset buffer pointer to the beginning
    buffer.seek(0)

    # Build the HTTP response for download
    response = HttpResponse(
        buffer,
        content_type='text/plain'  # or 'text/csv', but .ply is not a standard mime type
    )
    # Output file named with .ply extension
    filename = f"{schedule_date.strftime('%Y_%m_%d')}_00_00_00.ply"

    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



# @login_required
# @user_passes_test(lambda u: u.is_staff)
# def export_playlist(schedule_date):
#     """Export playlist with correct timezone handling"""
#     # schedule_date is a string if coming from the URL pattern;
#     # parse it to a proper date if necessary.
#     if isinstance(schedule_date, str):
#         schedule_date = datetime.strptime(schedule_date, '%Y-%m-%d').date()

#     buffer = io.StringIO()
#     writer = csv.writer(buffer)

#     utc = pytz.UTC
#     local_tz = pytz.timezone('America/New_York')

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
#         utc_datetime = episode.start_time.astimezone(utc)
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


# # import datetime
# # import io
# # import csv
# # import pytz
# # from django.http import HttpResponse


# def export_playlist(schedule_date):
#     """Export playlist with correct timezone handling"""
#     buffer = io.StringIO()
    
#     # Use semicolon delimiter without quoting
#     writer = csv.writer(buffer, delimiter=';', quoting=csv.QUOTE_NONE, escapechar='\\')
    
#     # Convert date to datetime at midnight if it's a date object
#     if isinstance(schedule_date, datetime.date):
#         local_tz = pytz.timezone('America/New_York')
#         schedule_date = datetime.datetime.combine(schedule_date, datetime.time.min)
#         schedule_date = local_tz.localize(schedule_date)
    
#     schedule = ScheduledEpisode.objects.filter(
#         schedule_date=schedule_date
#     ).order_by('start_time')
    
#     for episode in schedule:
#         # Convert duration timecode to seconds
#         duration_seconds = convert_timecode_to_seconds(episode.duration_timecode)
        
#         # Construct filepath using custom_id and file_name
#         filepath = f'Z:\\{episode.custom_id}\\{episode.file_name}'
        
#         # Format: filepath;start_time;duration;;title
#         writer.writerow([
#             f'"{filepath}"',  # Wrap filepath in quotes
#             f'{0.00000:,.5f}',  # Start time in seconds with 5 decimal places
#             f'{duration_seconds:,.5f}',  # Duration in seconds with 5 decimal places
#             '',  # Empty field before title
#             episode.title
#         ])
    
#     buffer.seek(0)
    
#     # Use the schedule_date which is now a datetime for filename
#     filename = schedule_date.strftime('%Y_%m_%d_%H_%M_%S.txt')
    
#     response = HttpResponse(buffer, content_type='text/plain')
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     return response

# def convert_timecode_to_seconds(timecode):
#     """Convert HH:MM:SS timecode to seconds with millisecond precision"""
#     hours, minutes, seconds = map(float, timecode.split(':'))
#     return hours * 3600 + minutes * 60 + seconds

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

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from .models import Episode, GENRE_CHOICES, AGE_RATING_CHOICES, Creator
import logging

logger = logging.getLogger(__name__)

class AvailableContentView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Episode
    template_name = 'available_content.html'
    context_object_name = 'episodes'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    # (1) This method is optional if we rely on the mixin’s test_func already,
    #     but we can keep it to ensure a 403 response if staff check fails.
    #     Otherwise, a non-staff user would be redirected by default. 
    #     That might be enough for your use case.

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        # user must already be staff by the time this is reached
        episode_id = request.POST.get('episode_id')
        field = request.POST.get('field')
        value = request.POST.get('value')

        logger.info(f"Updating Episode: {episode_id}, Field: {field}, Value: {value}")

        try:
            episode = get_object_or_404(Episode, custom_id=episode_id)
            if field == 'ready_for_air':
                episode.ready_for_air = (value.lower() == 'true')
            elif field == 'ai_age_rating':
                episode.ai_age_rating = value
            # Add more fields as needed

            episode.save()
            return JsonResponse({'status': 'success', 'new_value': getattr(episode, field)})

        except Exception as e:
            logger.error(f"Error updating episode {episode_id}: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def get_queryset(self):
        # Normal GET filtering logic
        queryset = Episode.objects.all()

        ready_for_air = self.request.GET.get('ready_for_air')
        if ready_for_air:
            if ready_for_air.lower() == 'true':
                queryset = queryset.filter(ready_for_air=True)
            elif ready_for_air.lower() == 'false':
                queryset = queryset.filter(ready_for_air=False)

        ai_genre = self.request.GET.get('ai_genre')
        if ai_genre:
            queryset = queryset.filter(ai_genre=ai_genre)

        ai_age_rating = self.request.GET.get('ai_age_rating')
        if ai_age_rating:
            queryset = queryset.filter(ai_age_rating=ai_age_rating)

        creator = self.request.GET.get('creator')
        if creator:
            queryset = queryset.filter(program__creator=creator)

        duration = self.request.GET.get('duration')
        if duration == 'bumper':
            queryset = queryset.filter(duration_seconds__lte=15)
        elif duration == 'shortform':
            queryset = queryset.filter(duration_seconds__gt=15, duration_seconds__lte=900)
        elif duration == 'longform':
            queryset = queryset.filter(duration_seconds__gt=900)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(program__program_name__icontains=search)
                | Q(program__creator__channel_name__icontains=search)
            )

        sort = self.request.GET.get('sort', '-created_at')
        # Optional: Validate sort to avoid malicious input
        queryset = queryset.order_by(sort)

        return queryset.select_related('program', 'program__creator')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filters'] = {
            'ai_genre': self.request.GET.get('ai_genre', ''),
            'ai_age_rating': self.request.GET.get('ai_age_rating', ''),
            'creator': self.request.GET.get('creator', ''),
            'duration': self.request.GET.get('duration', ''),
            'search': self.request.GET.get('search', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
            'ready_for_air': self.request.GET.get('ready_for_air', ''),
        }
        context['ai_genres'] = dict(GENRE_CHOICES)
        context['ai_age_ratings'] = dict(AGE_RATING_CHOICES)
        context['creators'] = Creator.objects.all()
        context['duration_choices'] = [
            ('bumper', 'Bumper (≤15s)'),
            ('shortform', 'Short Form (15s-15m)'),
            ('longform', 'Long Form (>15m)'),
        ]
        context['ready_for_air_choices'] = [
            ('', 'All Content'),
            ('true', 'Ready for Air'),
            ('false', 'Not Ready'),
        ]
        return context


# views.py
# from django.views.generic import ListView
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.db.models import Q
# from .models import Episode, GENRE_CHOICES, AGE_RATING_CHOICES, Creator

# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.utils.decorators import method_decorator
# from django.urls import path

# class AvailableContentView(LoginRequiredMixin, UserPassesTestMixin, ListView):
#     model = Episode
#     template_name = 'available_content.html'
#     context_object_name = 'episodes'
#     paginate_by = 20

#     def test_func(self):
#         return self.request.user.is_staff
    
#     def post(self, request, *args, **kwargs):
#         """Handle POST requests for updating episodes"""
#         logger.info("POST request received")  # Debug print
#         logger.info("POST data:", request.POST)  # Debug print
#         print("POST request received")  # Debug print
#         print("POST data:", request.POST)  # Debug print
        
#         if not request.user.is_staff:
#             return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
            
#         try:
#             episode_id = request.POST.get('episode_id')
#             field = request.POST.get('field')
#             value = request.POST.get('value')
            
#             logger.info(f"Updating episode {episode_id}, field {field} to value {value}")  # Debug print
#             print(f"Updating episode {episode_id}, field {field} to value {value}")  # Debug print
            
#             episode = Episode.objects.get(custom_id=episode_id)
            
#             if field == 'ready_for_air':
#                 episode.ready_for_air = value.lower() == 'true'
#             elif field == 'ai_age_rating':
#                 episode.ai_age_rating = value
            
#             episode.save()
#             logger.info(f"Save successful, new value: {getattr(episode, field)}")  # Debug print
#             print(f"Save successful, new value: {getattr(episode, field)}")  # Debug print
            
#             return JsonResponse({
#                 'status': 'success',
#                 'new_value': getattr(episode, field)
#             })
#         except Episode.DoesNotExist:
#             logger.info(f"Episode not found: {episode_id}")  # Debug print
#             print(f"Episode not found: {episode_id}")  # Debug print
#             return JsonResponse({'status': 'error', 'message': 'Episode not found'}, status=404)
#         except Exception as e:
#             logger.info(f"Error updating episode: {str(e)}")  # Debug print
#             print(f"Error updating episode: {str(e)}")  # Debug print
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


#     def get_queryset(self):
#         # queryset = Episode.objects.filter(ready_for_air=True)
#         queryset = Episode.objects.all()
#         # Add ready_for_air filter from GET parameters
#         ready_for_air = self.request.GET.get('ready_for_air')
#         if ready_for_air:
#             if ready_for_air.lower() == 'true':
#                 queryset = queryset.filter(ready_for_air=True)
#             elif ready_for_air.lower() == 'false':
#                 queryset = queryset.filter(ready_for_air=False)
#         # If no ready_for_air parameter is provided, show all episodes

#         # Apply filters from GET parameters
#         ai_genre = self.request.GET.get('ai_genre')
#         if ai_genre:
#             queryset = queryset.filter(ai_genre=ai_genre)
            
#         ai_age_rating = self.request.GET.get('ai_age_rating')
#         if ai_age_rating:
#             queryset = queryset.filter(ai_age_rating=ai_age_rating)
            
#         creator = self.request.GET.get('creator')
#         if creator:
#             queryset = queryset.filter(program__creator=creator)
            
#         duration = self.request.GET.get('duration')
#         if duration:
#             if duration == 'bumper':
#                 queryset = queryset.filter(duration_seconds__lte=15)
#             elif duration == 'shortform':
#                 queryset = queryset.filter(duration_seconds__gt=15, duration_seconds__lte=900)
#             elif duration == 'longform':
#                 queryset = queryset.filter(duration_seconds__gt=900)

#         # Apply search if provided
#         search = self.request.GET.get('search')
#         if search:
#             queryset = queryset.filter(
#                 Q(title__icontains=search) |
#                 Q(program__program_name__icontains=search) |
#                 Q(program__creator__channel_name__icontains=search)
#             )

#         # Apply sorting
#         sort = self.request.GET.get('sort', '-created_at')
#         queryset = queryset.order_by(sort)
        
#         return queryset.select_related('program', 'program__creator')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['current_filters'] = {
#             'ai_genre': self.request.GET.get('ai_genre', ''),
#             'ai_age_rating': self.request.GET.get('ai_age_rating', ''),
#             'creator': self.request.GET.get('creator', ''),
#             'duration': self.request.GET.get('duration', ''),
#             'search': self.request.GET.get('search', ''),
#             'sort': self.request.GET.get('sort', '-created_at'),
#             'ready_for_air': self.request.GET.get('ready_for_air', ''),  # Add this line
#         }
#         context['ai_genres'] = dict(GENRE_CHOICES)
#         context['ai_age_ratings'] = dict(AGE_RATING_CHOICES)
#         context['creators'] = Creator.objects.all()
#         context['duration_choices'] = [
#             ('bumper', 'Bumper (≤15s)'),
#             ('shortform', 'Short Form (15s-15m)'),
#             ('longform', 'Long Form (>15m)'),
#         ]
#         context['ready_for_air_choices'] = [
#             ('', 'All Content'),
#             ('true', 'Ready for Air'),
#             ('false', 'Not Ready'),
#         ]
#         return context
    
#     @method_decorator(require_POST)
#     def update_episode(self, request, *args, **kwargs):
#         try:
#             episode_id = request.POST.get('episode_id')
#             field = request.POST.get('field')
#             value = request.POST.get('value')
            
#             episode = Episode.objects.get(custom_id=episode_id)
            
#             if field == 'ready_for_air':
#                 episode.ready_for_air = value.lower() == 'true'
#             elif field == 'ai_age_rating':
#                 episode.ai_age_rating = value
            
#             episode.save()
            
#             return JsonResponse({
#                 'status': 'success',
#                 'new_value': getattr(episode, field)
#             })
#         except Episode.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Episode not found'}, status=404)
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        

# views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.core.paginator import Paginator

@staff_member_required
def admin_tickets(request):
    # Get filter parameters from request
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    urgency = request.GET.get('urgency', '')

    # Start with all tickets
    tickets = SupportTicket.objects.all().order_by('-time_received')

    # Apply filters
    if status:
        tickets = tickets.filter(ticket_status=status)
    if category:
        tickets = tickets.filter(category=category)
    if urgency:
        tickets = tickets.filter(urgency=urgency)
    if search:
        tickets = tickets.filter(
            Q(ticket_no__icontains=search) |
            Q(subject__icontains=search) |
            Q(name__icontains=search) |
            Q(contact_info__icontains=search)
        )

    # Pagination
    paginator = Paginator(tickets, 25)  # Show 25 tickets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tickets': page_obj,
        'status_choices': SupportTicket.STATUS_CHOICES,
        'category_choices': SupportTicket.TICKET_CATEGORIES,
        'urgency_choices': SupportTicket.URGENCY_CHOICES,
        'selected_status': status,
        'selected_category': category,
        'selected_urgency': urgency,
        'search_query': search,
    }
    
    return render(request, 'support/admin_tickets.html', context)


# views.py
@staff_member_required
def update_ticket_status(request, ticket_no):
    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, ticket_no=ticket_no)
        new_status = request.POST.get('ticket_status')
        if new_status in dict(SupportTicket.STATUS_CHOICES):
            ticket.ticket_status = new_status
            ticket.save()
    return redirect('admin_tickets')


@login_required
def delete_episode(request, episode_id):
    logger.info(f"Delete episode request received for episode_id: {episode_id}")
    
    try:
        episode = get_object_or_404(Episode, custom_id=episode_id)
        logger.info(f"Episode found: {episode.title} (ID: {episode.custom_id})")
        
        # Security check: ensure the user owns this episode
        if episode.created_by != request.user:
            logger.warning(f"Unauthorized delete attempt for episode {episode_id} by user {request.user}")
            return HttpResponse("Unauthorized", status=401)
        
        if request.method == 'POST':
            logger.info(f"Processing POST request to delete episode {episode_id}")
            
            # If the episode has a file, delete it from S3
            if episode.file_name:
                try:
                    logger.info(f"Attempting to delete S3 file: {episode.file_name}")
                    s3_client = boto3.client('s3')
                    s3_client.delete_object(
                        Bucket=AWS_STORAGE_BUCKET_NAME,
                        Key=episode.file_name
                    )
                    logger.info("S3 file deleted successfully")
                except Exception as e:
                    logger.error(f"Error deleting S3 file: {str(e)}", exc_info=True)
                    messages.error(request, f"Error deleting file from S3: {str(e)}")
                    return redirect('my-episodes')
            
            try:
                # Delete any associated media info records first
                media_info_count = EpisodeMediaInfo.objects.filter(episode=episode).count()
                logger.info(f"Found {media_info_count} media info records to delete")
                EpisodeMediaInfo.objects.filter(episode=episode).delete()
                logger.info("Media info records deleted successfully")
                
                # Delete the episode
                logger.info(f"Attempting to delete episode {episode_id} from database")
                episode.delete()
                logger.info(f"Episode {episode_id} successfully deleted from database")
                
                messages.success(request, "Episode successfully deleted.")
                return redirect('my-episodes')
            except Exception as e:
                logger.error(f"Error deleting episode from database: {str(e)}", exc_info=True)
                messages.error(request, f"Error deleting episode: {str(e)}")
                return redirect('my-episodes')
        else:
            logger.warning(f"Non-POST request received for episode deletion: {request.method}")
        
        return redirect('my-episodes')
        
    except Episode.DoesNotExist:
        logger.error(f"Episode not found: {episode_id}")
        messages.error(request, "Episode not found.")
        return redirect('my-episodes')
    except Exception as e:
        logger.error(f"Unexpected error in delete_episode: {str(e)}", exc_info=True)
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('my-episodes')
    
@login_required
def delete_program(request, program_id):
    logger.info(f"Delete program request received for program_id: {program_id}")
    
    try:
        program = get_object_or_404(Program, custom_id=program_id)
        logger.info(f"Program found: {program.program_name} (ID: {program.custom_id})")
        
        # Security check: ensure the user owns this program
        if program.created_by != request.user:
            logger.warning(f"Unauthorized delete attempt for program {program_id} by user {request.user}")
            return HttpResponse("Unauthorized", status=401)
        
        # Check if program has any episodes
        episode_count = Episode.objects.filter(program=program).count()
        if episode_count > 0:
            logger.warning(f"Attempted to delete program {program_id} with {episode_count} episodes")
            messages.error(request, "Cannot delete program with existing episodes")
            return redirect('my-programs')
        
        if request.method == 'POST':
            logger.info(f"Processing POST request to delete program {program_id}")
            
            try:
                # Delete the program
                program.delete()
                logger.info(f"Program {program_id} successfully deleted from database")
                messages.success(request, "Program successfully deleted.")
                return redirect('my-programs')
            except Exception as e:
                logger.error(f"Error deleting program from database: {str(e)}", exc_info=True)
                messages.error(request, f"Error deleting program: {str(e)}")
                return redirect('my-programs')
        
        return redirect('my-programs')
        
    except Program.DoesNotExist:
        logger.error(f"Program not found: {program_id}")
        messages.error(request, "Program not found.")
        return redirect('my-programs')
    except Exception as e:
        logger.error(f"Unexpected error in delete_program: {str(e)}", exc_info=True)
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('my-programs')