import logging
from django.shortcuts import render, redirect, get_object_or_404
from .models import Creator, Program, Episode
from .forms import CreatorForm, ProgramForm, EpisodeForm, EpisodeUploadForm, EpisodeUpdateForm
from django.http import HttpResponseRedirect, HttpResponse
from .utils import create_presigned_url  # Assuming the function is in utils.py
from django.contrib import messages
from pprint import pprint
import requests

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
def home(request):
    user_has_creator = Creator.objects.filter(created_by=request.user).exists() if request.user.is_authenticated else False
    return render(request, 'home.html', {'user_has_creator': user_has_creator})

def homepage(request):
    user_has_programs = False
    if request.user.is_authenticated:
        # Check if the user has any programs
        user_has_programs = Program.objects.filter(created_by=request.user).exists()
    return render(request, 'homepage.html', {'user_has_programs': user_has_programs})

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


# def add_episode(request):
#     submitted = False
#     form = EpisodeForm()
#     if request.method == 'POST':
#         form = EpisodeForm(request.POST, user=request.user)  # Pass user to the form
#         if form.is_valid():
#             instance = form.save(commit=False)  # Create an instance without saving to the database
#             instance.created_by = request.user  # Set the created_by field to the current user
#             instance.save()  # Now save the instance to the database
#             return HttpResponseRedirect('/add_episode?submitted=True')
#     else:
#         form = EpisodeForm(user=request.user)
#         if 'submitted' in request.GET:
#             submitted = True
#     return render(request, 'add_episode.html', {'form': form, 'submitted': submitted})



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
            bucket_name = 'channel24-3dbcad81-2747-4a18-acdd-68ae14b4fa71'  # Replace with your actual S3 bucket name

            # Generate a unique file name/path
            unique_file_name = f'episodes/{episode.custom_id}/{file_name}'

            # Generate the pre-signed URL
            presigned_url = create_presigned_url(bucket_name, unique_file_name)

            if presigned_url:
                # Upload the file to S3 using the pre-signed URL
                response = requests.put(presigned_url, data=file)
                if response.status_code == 200:
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


def upload_success(request):
    return render(request, 'upload_success.html')

