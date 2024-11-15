import logging
from django.shortcuts import render, redirect, get_object_or_404
from .models import Creator, Program, Episode, EpisodeMediaInfo
from .forms import CreatorForm, ProgramForm, EpisodeForm, EpisodeUploadForm, EpisodeUpdateForm
from django.http import HttpResponseRedirect, HttpResponse
from .utils import create_presigned_url  # Assuming the function is in utils.py
from django.contrib import messages
from pprint import pprint
import requests
import boto3
from pymediainfo import MediaInfo

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
    temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp', os.path.basename(s3_key))

    print('Temp file path: ', temp_file_path)

    # Download the file from S3
    s3.download_file(bucket_name, s3_key, temp_file_path)

    # Use pymediainfo to get media information
    media_info = MediaInfo.parse(temp_file_path)
    # pprint(media_info)

    # Clean up the temporary file
    os.remove(temp_file_path)

    return media_info


def upload_episode(request, episode_id):
    episode = get_object_or_404(Episode, custom_id=episode_id)

    # Security check: Ensure the user is the creator of the episode
    if episode.created_by != request.user:
        return HttpResponse("Unauthorized", status=401)

    if request.method == 'POST':
        form = EpisodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_name = file.name
            
            bucket_name = AWS_STORAGE_BUCKET_NAME
            print(f"bucket_name: {bucket_name}")

            # Generate a unique file name/path
            unique_file_name = f'episodes/{episode.custom_id}/{file_name}'

            # Generate the pre-signed URL
            presigned_url = create_presigned_url(bucket_name, unique_file_name)

            if presigned_url:
                # Upload the file to S3 using the pre-signed URL
                response = requests.put(presigned_url, data=file)
                print(f"Response: {response}")
                if response.status_code == 200:
                    # Get media info from the uploaded file
                    media_info = get_mediainfo_from_s3(bucket_name, unique_file_name)
                    
                    # Log and save media info for each track
                    track_id = 0
                    for track in media_info.tracks:
                        track_id += 1
                        pprint(track.to_data())
                        track_metadata = {key: value for key, value in track.to_data().items() if value is not None}
                        logger.debug(f"Track {track_id}: {track_metadata}")

                        # Save media info to the database
                        EpisodeMediaInfo.objects.create(
                            episode=episode,
                            track_id=track_id,
                            metadata=track_metadata
                        )

                    # Update the episode with the file name
                    episode.file_name = unique_file_name
                    episode.save()
                    messages.success(request, "File uploaded successfully.")
                    return redirect('upload_success')
                else:
                    print(f"Failed to upload: {response.content}")
                    messages.error(request, "Upload failed.")
            else:
                print("Unable to generate upload URL.")
                messages.error(request, "Unable to generate upload URL.")
        else:
            print("Form is invalid")
            print(form.errors)
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
#             file = form.cleaned_data['file']
#             file_name = file.name
#             bucket_name = 'channel24-3dbcad81-2747-4a18-acdd-68ae14b4fa71'  # Replace with your actual S3 bucket name

#             # Generate a unique file name/path
#             unique_file_name = f'episodes/{episode.custom_id}/{file_name}'

#             # Generate the pre-signed URL
#             presigned_url = create_presigned_url(bucket_name, unique_file_name)

#             if presigned_url:
#                 # Upload the file to S3 using the pre-signed URL
#                 response = requests.put(presigned_url, data=file)
#                 if response.status_code == 200:
#                     # Get media info from the uploaded file
#                     media_info = get_mediainfo_from_s3(bucket_name, unique_file_name)
#                     pprint(media_info.to_data())  # Print or process the media info as needed

#                     # Update the episode with the file name
#                     episode.file_name = unique_file_name
#                     episode.save()
#                     messages.success(request, "File uploaded successfully.")
#                     return redirect('upload_success')
#                 else:
#                     print(f"Failed to upload: {response.content}")
#                     messages.error(request, "Upload failed.")
#             else:
#                 print("Unable to generate upload URL.")
#                 messages.error(request, "Unable to generate upload URL.")
#         else:
#             print("Form is invalid")
#             print(form.errors)
#             messages.error(request, "Form is invalid.")
#     else:
#         form = EpisodeUploadForm()

#     return render(request, 'episode_upload.html', {'form': form, 'episode': episode})


# def upload_episode(request, episode_id):
#     episode = get_object_or_404(Episode, custom_id=episode_id)

#     # Security check: Ensure the user is the creator of the episode
#     if episode.created_by != request.user:
#         return HttpResponse("Unauthorized", status=401)

#     if request.method == 'POST':
#         form = EpisodeUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             file = form.cleaned_data['file']
#             file_name = file.name
#             get_medininfo(file_name)
#             bucket_name = 'channel24-3dbcad81-2747-4a18-acdd-68ae14b4fa71'  # Replace with your actual S3 bucket name

#             # Generate a unique file name/path
#             unique_file_name = f'episodes/{episode.custom_id}/{file_name}'

#             # Generate the pre-signed URL
#             presigned_url = create_presigned_url(bucket_name, unique_file_name)

#             if presigned_url:
#                 # Upload the file to S3 using the pre-signed URL
#                 response = requests.put(presigned_url, data=file)
#                 if response.status_code == 200:
#                     # Update the episode with the file name
#                     episode.file_name = unique_file_name
#                     episode.save()
#                     messages.success(request, "File uploaded successfully.")
#                     return redirect('upload_success')
#                 else:
#                     print(f"Failed to upload: {response.content}")
#                     messages.error(request, "Upload failed.")
#             else:
#                 print("Unable to generate upload URL.")
#                 messages.error(request, "Unable to generate upload URL.")
#         else:
#             print("Form is invalid")
#             print(form.errors)
#             messages.error(request, "Form is invalid.")
#     else:
#         form = EpisodeUploadForm()

#     return render(request, 'episode_upload.html', {'form': form, 'episode': episode})      


def upload_success(request):
    return render(request, 'upload_success.html')


def adobe_premiere(request):
    return render(request, 'adobe_premiere.html')

def davinci_resolve(request):
    return render(request, 'davinci_resolve.html')

def getting_started(request):
    return render(request, 'getting_started.html')

import os

def episode_media_info(request, episode_id):
    print("episode_media_info")
    episode = get_object_or_404(Episode, custom_id=episode_id)
    media_infos = episode.media_infos.all()

    # Use sets to track unique error and warning messages
    unique_errors = set()
    unique_warnings = set()

    # Define media_checks data structure for flexibility
    media_checks = {
        'General': {
            'max_duration': 3600,  # Maximum duration in seconds (60 minutes)
            'allowed_extensions': ['mp4', 'mov']  # Allowed file extensions
        },
        'Video': {
            'height_checks': [
                {
                    'height_range': (710, 730),
                    'bitrate_range': (5000000, 7500000),
                    'target_height': 720,
                    'bitrate_error_level': 'WARNING'
                },
                {
                    'height_range': (1070, 1090),
                    'bitrate_range': (8000000, 12000000),  # 8–12 Mbps
                    'target_height': 1080,
                    'bitrate_error_level': 'WARNING'
                }
                # Additional height checks can be added here
            ],
            'acceptable_frame_rates': [23.976, 23.98, 29.97],
            'frame_rate_error_level': 'WARNING',
            'height_error_level': 'WARNING'
        },
        'Audio': {
            'bitrate_range': (128000, 320000),  # 128–320 Kbps
            'channels': [1, 2],                 # One or two audio channels
            'sampling_rates': [48000]           # Sampling rate should be 48000 Hz
        }  # Add closing brace here
    }  # Missing closing brace for media_checks dictionary

    for media_info in media_infos:
        metadata = media_info.metadata
        track_type = metadata.get('track_type', None)

        if track_type == 'General':
            # print(f"Checking {track_type} track")
            # Get duration
            duration = metadata.get('duration', None)
            # Convert duration to float
            try:
                duration = float(duration) if duration is not None else None
            except ValueError:
                duration = None

            if duration is not None:
                max_duration = media_checks[track_type]['max_duration']
                if duration > max_duration:
                    duration_minutes = duration / 60  # Convert to minutes for display
                    max_duration_minutes = max_duration / 60
                    error_message = (
                        f"The media duration is {duration_minutes:.2f} minutes, which exceeds the maximum allowed duration of "
                        f"{max_duration_minutes} minutes."
                    )
                    unique_errors.add(error_message)
            else:
                error_message = "Media duration is missing."
                unique_errors.add(error_message)

            # Get file extension
            file_name = episode.file_name  # Assuming episode.file_name exists
            if file_name:
                _, ext = os.path.splitext(file_name)
                ext = ext.lower().lstrip('.')
                allowed_extensions = media_checks[track_type]['allowed_extensions']
                if ext not in allowed_extensions:
                    error_message = f"File extension '{ext}' is not allowed. Allowed extensions are: {', '.join(allowed_extensions)}."
                    unique_errors.add(error_message)
            else:
                error_message = "File name is missing."
                unique_errors.add(error_message)

        elif track_type == 'Video':
            # print(f"Checking {track_type} track")
            # Get height, bit_rate, frame_rate
            height = metadata.get('height', None)
            bit_rate = metadata.get('bit_rate', None)
            frame_rate = metadata.get('frame_rate', None)

            # Convert to appropriate numeric types
            try:
                height = float(height) if height is not None else None
            except ValueError:
                height = None
            try:
                bit_rate = float(bit_rate) if bit_rate is not None else None
            except ValueError:
                bit_rate = None
            try:
                frame_rate = float(frame_rate) if frame_rate is not None else None
            except ValueError:
                frame_rate = None

            # Initialize a flag to indicate if height matched any defined range
            height_matched = False

            # Check height to determine which bitrate range to use
            if height is not None:
                for height_check in media_checks[track_type]['height_checks']:
                    min_height, max_height = height_check['height_range']
                    if min_height <= height <= max_height:
                        height_matched = True
                        target_height = height_check['target_height']
                        min_bitrate, max_bitrate = height_check['bitrate_range']
                        # Now check bitrate
                        if bit_rate is not None:
                            if not (min_bitrate <= bit_rate <= max_bitrate):
                                warning_message = (
                                    f"Video track with height {target_height} pixels should have a bitrate between "
                                    f"{min_bitrate / 1_000_000}–{max_bitrate / 1_000_000} Mbps, but has "
                                    f"{bit_rate / 1_000_000:.2f} Mbps."
                                )
                                unique_warnings.add(warning_message)
                        else:
                            warning_message = "Video track bitrate is missing."
                            unique_warnings.add(warning_message)
                        break  # Exit the loop after finding a matching height range
                if not height_matched:
                    error_message = f"Video track has unexpected height {height} pixels."
                    unique_errors.add(error_message)
            else:
                error_message = "Video track height is missing."
                unique_errors.add(error_message)

            # Check frame_rate
            acceptable_frame_rates = media_checks[track_type]['acceptable_frame_rates']
            if frame_rate is not None:
                frame_rate_ok = any(abs(frame_rate - fr) < 0.1 for fr in acceptable_frame_rates)
                if not frame_rate_ok:
                    warning_message = (
                        f"Video track frame rate should be 29.97 or 23.98 fps, but is {frame_rate} fps."
                    )
                    unique_warnings.add(warning_message)
            else:
                warning_message = "Video track frame rate is missing."
                unique_warnings.add(warning_message)

        elif track_type == 'Audio':
            # print(f"Checking {track_type} track")
            # Get bit_rate, channels, sampling_rate
            bit_rate = metadata.get('bit_rate', None)
            channels = metadata.get('channel_s', None)
            sampling_rate = metadata.get('sampling_rate', None)

            # Convert to appropriate numeric types
            try:
                bit_rate = float(bit_rate) if bit_rate is not None else None
            except ValueError:
                bit_rate = None
            try:
                channels = int(channels) if channels is not None else None
            except ValueError:
                channels = None
            try:
                sampling_rate = int(sampling_rate) if sampling_rate is not None else None
            except ValueError:
                sampling_rate = None

            # Check bit_rate
            if bit_rate is not None:
                min_bitrate, max_bitrate = media_checks[track_type]['bitrate_range']
                if not (min_bitrate <= bit_rate <= max_bitrate):
                    warning_message = (
                        f"Audio track bitrate should be between "
                        f"{min_bitrate / 1000}–{max_bitrate / 1000} kbps, but is "
                        f"{bit_rate / 1000:.2f} kbps."
                    )
                    unique_warnings.add(warning_message)
            else:
                warning_message = "Audio track bitrate is missing."
                unique_warnings.add(warning_message)

            # Check channels
            if channels is not None:
                if channels not in media_checks[track_type]['channels']:
                    error_message = (
                        f"Audio track should have {media_checks[track_type]['channels']} channels, but has {channels} channels."
                    )
                    unique_errors.add(error_message)
            else:
                warning_message = "Audio track channel count is missing."
                unique_warnings.add(warning_message)

            # Check sampling_rate
            if sampling_rate is not None:
                if sampling_rate not in media_checks[track_type]['sampling_rates']:
                    error_message = (
                        f"Audio track sampling rate should be {media_checks[track_type]['sampling_rates'][0]} Hz, but is {sampling_rate} Hz."
                    )
                    unique_errors.add(error_message)
            else:
                warning_message = "Audio track sampling rate is missing."
                unique_warnings.add(warning_message)

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
