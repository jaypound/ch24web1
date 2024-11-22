import logging
from django.shortcuts import render, redirect, get_object_or_404
from .models import Creator, Program, Episode, EpisodeMediaInfo
from .forms import CreatorForm, ProgramForm, EpisodeForm, EpisodeUploadForm, EpisodeUpdateForm
from django.http import HttpResponseRedirect, HttpResponse
from .utils import create_presigned_url  # Assuming the function is in utils.py
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import requests
import boto3
from pymediainfo import MediaInfo
from .utils import validate_media_info  # Import the validation function

import os
from django.conf import settings

AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

# from .models import MediaInfo

logger = logging.getLogger('django')
# Get an instance of a logger
# logger = logging.getLogger(__name__)

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

def add_program(request):
    submitted = False
    if request.method == 'POST':
        form = ProgramForm(request.POST, user=request.user)  # Pass user to the form
        if form.is_valid():
            instance = form.save(commit=False)  # Create an instance without saving to the database
            instance.created_by = request.user  # Set the created_by field to the current user
            instance.save()  # Now save the instance to the database
            return HttpResponseRedirect('/add_program?submitted=True')
    else:
        form = ProgramForm(user=request.user)  # Pass user to the form
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_program.html', {'form': form, 'submitted': submitted})


def add_episode(request):
    submitted = False
    if request.method == 'POST':
        form = EpisodeForm(request.POST, user=request.user)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            return HttpResponseRedirect('/add_episode?submitted=True')
    else:
        # Get the last program added by the current user using 'created_at'
        # Prepare initial data for the form
        initial_data = {}
        last_program = Program.objects.filter(created_by=request.user).order_by('-created_at').first()
        if not last_program:
            messages.error(request, "You need to add a program before adding episodes.")
            program_form = ProgramForm(user=request.user)
            submitted = False
            return render(request, 'add_program.html', {'form': program_form, 'submitted': submitted})        

        if last_program:
            initial_data['program'] = last_program  # Pre-fill the 'program' field

        form = EpisodeForm(user=request.user, initial=initial_data)
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_episode.html', {'form': form, 'submitted': submitted})

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

def update_program(request, program_id):
    program = Program.objects.get(custom_id=program_id)  # Changed from id to custom_id
    if request.method == "POST":
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return render(request, 'update_program.html', {
                'form': form,
                'submitted': True
            })
    else:
        form = ProgramForm(instance=program)
    
    return render(request, 'update_program.html', {
        'form': form,
        'submitted': False
    })

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

    # print('Temp file path: ', temp_file_path)

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

            # Generate a unique file name/path
            unique_file_name = f'episodes/{episode.custom_id}/{file_name}'

            # Generate the pre-signed URL
            presigned_url = create_presigned_url(bucket_name, unique_file_name)

            if presigned_url:
                # Upload the file to S3 using the pre-signed URL
                response = requests.put(presigned_url, data=file)
                if response.status_code == 200:
                    # Get media info from the uploaded file
                    media_info = get_mediainfo_from_s3(bucket_name, unique_file_name)

                    # Save media info to the database
                    track_id = 0
                    for track in media_info.tracks:
                        track_id += 1
                        track_metadata = {key: value for key, value in track.to_data().items() if value is not None}

                        # Save media info to the database
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

                    # Redirect without the mediainfo_errors flag
                    return redirect(f"{reverse('upload_success')}?episode_id={episode.custom_id}")
                else:
                    messages.error(request, "Upload failed.")
                    return redirect('upload_failed')
            else:
                messages.error(request, "Unable to generate upload URL.")
                return redirect('upload_failed')
        else:
            messages.error(request, "Form is invalid.")
    else:
        form = EpisodeUploadForm()

    return render(request, 'episode_upload.html', {'form': form, 'episode': episode})


# def upload_episode(request, episode_id):
#     episode = get_object_or_404(Episode, custom_id=episode_id)

#     # Security check: Ensure the user is the creator of the episode
#     if episode.created_by != request.user:
#         return HttpResponse("Unauthorized", status=401)

#     if request.method == 'POST':
#         form = EpisodeUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Delete previous EpisodeMediaInfo instances
#             EpisodeMediaInfo.objects.filter(episode=episode).delete()

#             file = form.cleaned_data['file']
#             file_name = file.name
            
#             bucket_name = AWS_STORAGE_BUCKET_NAME
#             print(f"bucket_name: {bucket_name}")

#             # Generate a unique file name/path
#             unique_file_name = f'episodes/{episode.custom_id}/{file_name}'

#             # Generate the pre-signed URL
#             presigned_url = create_presigned_url(bucket_name, unique_file_name)

#             if presigned_url:
#                 # Upload the file to S3 using the pre-signed URL
#                 response = requests.put(presigned_url, data=file)
#                 print(f"Response: {response}")
#                 if response.status_code == 200:
#                     # Get media info from the uploaded file
#                     media_info = get_mediainfo_from_s3(bucket_name, unique_file_name)
                    
#                     # Log and save media info for each track
#                     track_id = 0
#                     for track in media_info.tracks:
#                         track_id += 1
#                         pprint(track.to_data())
#                         track_metadata = {key: value for key, value in track.to_data().items() if value is not None}
#                         logger.debug(f"Track {track_id}: {track_metadata}")

#                         # Save media info to the database
#                         EpisodeMediaInfo.objects.create(
#                             episode=episode,
#                             track_id=track_id,
#                             metadata=track_metadata
#                         )

#                     # Retrieve the saved media_infos
#                     media_infos = episode.media_infos.all()

#                     # Use the validation function
#                     unique_errors, unique_warnings = validate_media_info(media_infos)

#                     # Determine if there are any errors
#                     mediainfo_errors = bool(unique_errors)


#                     # Update the episode with the file name
#                     episode.file_name = unique_file_name
#                     episode.save()
#                     messages.success(request, "File uploaded successfully.")
#                     # return redirect('upload_success')
#                     # return redirect(f"{reverse('upload_success')}?episode_id={episode.custom_id}")

#                     return redirect(f"{reverse('upload_success')}?episode_id={episode.custom_id}&mediainfo_errors={int(mediainfo_errors)}")


#                 else:
#                     print(f"Failed to upload: {response.content}")
#                     messages.error(request, "Upload failed.")
#                     return redirect('upload_failed')
#             else:
#                 print("Unable to generate upload URL.")
#                 messages.error(request, "Unable to generate upload URL.")
#                 return redirect('upload_failed')
#         else:
#             print("Form is invalid")
#             print(form.errors)
#             messages.error(request, "Form is invalid.")
#     else:
#         form = EpisodeUploadForm()

#     return render(request, 'episode_upload.html', {'form': form, 'episode': episode})


def upload_success(request):
    episode_id = request.GET.get('episode_id')
    episode = get_object_or_404(Episode, custom_id=episode_id) if episode_id else None

    return render(request, 'upload_success.html', {
        'episode': episode,
    })



# def upload_success(request):
#     episode_id = request.GET.get('episode_id')
#     mediainfo_errors = bool(int(request.GET.get('mediainfo_errors', '0')))
#     episode = get_object_or_404(Episode, custom_id=episode_id) if episode_id else None

#     return render(request, 'upload_success.html', {
#         'episode': episode,
#         'mediainfo_errors': mediainfo_errors
#     })


def upload_failed(request):
    return render(request, 'upload_failed.html')

def adobe_premiere(request):
    return render(request, 'adobe_premiere.html')

def davinci_resolve(request):
    return render(request, 'davinci_resolve.html')

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
        'media_infos': media_infos
    })

# def episode_media_info(request, episode_id):
#     # print("episode_media_info")
#     episode = get_object_or_404(Episode, custom_id=episode_id)
#     media_infos = episode.media_infos.all()

#     unique_errors, unique_warnings = validate_media_info(media_infos)

#     # Add unique error messages to the Django messages framework as errors
#     for message in unique_errors:
#         messages.error(request, message)

#     # Add unique warning messages to the Django messages framework as warnings
#     for message in unique_warnings:
#         messages.warning(request, message)


#     return render(request, 'episode_media_info.html', {
#         'episode': episode,
#         'media_infos': media_infos,
#         'errors': unique_errors,
#         'warnings': unique_warnings
#     })

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


