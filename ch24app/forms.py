from django import forms
from django.forms import ModelForm
from .models import Program, Episode, Creator, EpisodeMediaInfo, SupportTicket, TicketResponse

class CreatorForm(ModelForm):
    class Meta:
        model = Creator
        fields = ['first_name', 'last_name', 'channel_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code']

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'channel_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control' }),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
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
    creator = forms.ModelChoiceField(
        queryset=Creator.objects.none(),  # Initial empty queryset
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Channel Name'
    )
    
    time_slots_requested = forms.MultipleChoiceField(
        choices=TIME_SLOTS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label='Time Slots Requested',
    )

    class Meta:
        model = Program
        fields = ['creator', 'program_name', 'description', 'genre', 'age_rating', 'time_slots_requested']
        widgets = {
            'program_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'age_rating': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProgramForm, self).__init__(*args, **kwargs)
        
        # Set the creator queryset based on the user
        if user:
            self.fields['creator'].queryset = Creator.objects.filter(created_by=user)

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

        widgets = {
            'program': forms.Select(attrs={'class': 'form-control'}),
            'episode_number': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control'}),
            # 'duration_seconds': forms.TextInput(attrs={'class': 'form-control'}),
            # 'duration_timecode': forms.TextInput(attrs={'class': 'form-control'}),
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


# forms.py

from django import forms
from .models import Episode

class EpisodeAnalysisForm(forms.ModelForm):
    
    class Meta:
        model = Episode
        fields = [
            'program',
            'episode_number',
            'title',
            'has_mediainfo_errors',
            'transcription',
            'ai_summary',
            'ai_genre',
            'ai_age_rating',
            'ai_topics',
            'ai_time_slots_recommended',
            'audience_engagement_score',
            'audience_engagement_reasons',
            'prohibited_content',
            'prohibited_content_reasons',
            'ready_for_air',
            'last_timeslot',
            'last_scheduled',
            'schedule_count',
            'duration_seconds',
            'duration_timecode',
        ]
        widgets = {
            'program': forms.Select(attrs={'class': 'form-control'}),
            'episode_number': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'has_mediainfo_errors': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'transcription': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'ai_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ai_genre': forms.TextInput(attrs={'class': 'form-control'}),
            'ai_age_rating': forms.TextInput(attrs={'class': 'form-control'}),
            'ai_topics': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ai_time_slots_recommended': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'audience_engagement_score': forms.TextInput(attrs={'class': 'form-control'}),
            'audience_engagement_reasons': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prohibited_content': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prohibited_content_reasons': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ready_for_air': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'last_timeslot': forms.TextInput(attrs={'class': 'form-control'}),
            'last_scheduled': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'schedule_count': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_seconds': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_timecode': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EpisodeAnalysisForm, self).__init__(*args, **kwargs)
        # Disable all fields to make them read-only
        for field in self.fields.values():
            field.disabled = True




class EpisodeUpdateForm(ModelForm):
    class Meta:
        model = Episode
        fields = ['program', 'episode_number', 'title', 'description', 'start_date', 'end_date', 'duration_seconds', 'duration_timecode']

        widgets = {
            'program': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Program'}),
            'episode_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Episode Number'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Start Date'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'End Date'}),
            'duration_seconds': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Duration in Seconds'}),
            'duration_timecode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Duration Timecode'}),
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

