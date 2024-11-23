from django import forms
from django.forms import ModelForm
from .models import Program, Episode, Creator, EpisodeMediaInfo, SupportTicket, TicketResponse

class CreatorForm(ModelForm):
    class Meta:
        model = Creator
        fields = ['first_name', 'last_name', 'channel_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code']
        labels = {
            'first_name': '',
            'last_name': '',
            'channel_name': '',
            'email': '',
            'phone': '',
            'address': '',
            'city': '',
            'state': '',
            'zip_code': '',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'channel_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Channel Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip Code'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CreatorForm, self).__init__(*args, **kwargs)


# forms.py

from django import forms
from django.forms import ModelForm
from .models import Program, TIME_SLOTS_CHOICES
from .models import Creator

class ProgramForm(ModelForm):
    time_slots_requested = forms.MultipleChoiceField(
        choices=TIME_SLOTS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Time Slots Requested',
    )

    class Meta:
        model = Program
        fields = ['program_name', 'description', 'genre', 'age_rating', 'time_slots_requested']
        labels = {
            'program_name': '',
            'description': '',
            'genre': '',
            'age_rating': '',
            'time_slots_requested': '',
        }
        widgets = {
            'program_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Program Name'}),
            # 'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),  # Set fewer rows
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'age_rating': forms.Select(attrs={'class': 'form-control'}),
            # The widget for 'time_slots_requested' is specified in the field declaration
        }

    def __init__(self, *args, **kwargs):
        super(ProgramForm, self).__init__(*args, **kwargs)
        # Remove handling of 'creator' since it's no longer in the form

        # Handle initial values for `time_slots_requested`
        if self.instance and self.instance.time_slots_requested:
            self.initial['time_slots_requested'] = self.instance.time_slots_requested.split(',')

    def save(self, commit=True):
        instance = super(ProgramForm, self).save(commit=False)
        # Get the cleaned data for `time_slots_requested`
        time_slots = self.cleaned_data.get('time_slots_requested', [])
        # Join the list into a comma-separated string
        instance.time_slots_requested = ','.join(time_slots)
        if commit:
            instance.save()
        return instance


class EpisodeForm(ModelForm):
    class Meta:
        model = Episode
        fields = ['program', 'episode_number', 'title', 'description', 'start_date', 'end_date']
        labels = {
            'program': '',
            'episode_number': '',
            'title': '',
            'description': '',
            'start_date': '',
            'end_date': '',
        }
        widgets = {
            'program': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Program'}),
            'episode_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Episode Number'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Start Date'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'End Date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EpisodeForm, self).__init__(*args, **kwargs)
        if user:
            print('User:', user)
            # Filter creators by the current user
            self.fields['program'].queryset = Program.objects.filter(created_by=user)
            # Debugging line to check the queryset
            print("Filtered programs for user:", user, self.fields['program'].queryset)
            # Set default to the first creator
            programs = self.fields['program'].queryset
            if programs.exists():
                self.fields['program'].initial = programs.first()
            else:
                print('No programs found')



class EpisodeUpdateForm(ModelForm):
    class Meta:
        model = Episode
        fields = ['program', 'episode_number', 'title', 'description', 'start_date', 'end_date']
        labels = {
            'program': '',
            'episode_number': '',
            'title': '',
            'description': '',
            'start_date': '',
            'end_date': '',
        }
        widgets = {
            'program': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Program'}),
            'episode_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Episode Number'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Start Date'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'End Date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EpisodeUpdateForm, self).__init__(*args, **kwargs)
        if user:
            print('User:', user)
            # Filter creators by the current user
            self.fields['program'].queryset = Program.objects.filter(created_by=user)
            # Debugging line to check the queryset
            print("Filtered programs for user:", user, self.fields['program'].queryset)
            # Set default to the first creator
            programs = self.fields['program'].queryset
            if programs.exists():
                self.fields['program'].initial = programs.first()
            else:
                print('No programs found')


class EpisodeUploadForm(forms.Form):
    file = forms.FileField(
        # label='Select episode to upload',
        label='',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
        })
    )


class EpisodeUploadForm2(forms.Form):
    file = forms.FileField(
        # label='Select episode to upload',
        label='',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
        })
    )

class EpisodeMediaInfoForm(ModelForm):
    class Meta:
        model = EpisodeMediaInfo
        fields = ['episode', 'track_id', 'metadata']


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['name', 'contact_info', 'category', 'subject', 'description', 'urgency', 'program', 'episode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Info'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'urgency': forms.Select(attrs={'class': 'form-control'}),
            'program': forms.Select(attrs={'class': 'form-control'}),
            'episode': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SupportTicketForm, self).__init__(*args, **kwargs)
        if user and user.is_authenticated:
            creator = Creator.objects.filter(created_by=user).first()
            if creator:
                self.fields['name'].initial = f"{creator.first_name} {creator.last_name}"
                self.fields['contact_info'].initial = creator.email
            else:
                self.fields['contact_info'].initial = user.email


class SupportTicketStatusForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['ticket_status']


class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

