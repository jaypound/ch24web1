from django import forms
from django.forms import ModelForm
from .models import Program, Episode, Creator, EpisodeMediaInfo, SupportTicket, TicketResponse

class CreatorForm(ModelForm):
    class Meta:
        model = Creator
        fields = ['first_name', 'last_name', 'company', 'email', 'phone', 'address', 'city', 'state', 'zip_code']
        labels = {
            'first_name': '',
            'last_name': '',
            'company': '',
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
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company'}),
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



class ProgramForm(ModelForm):
    class Meta:
        model = Program
        fields = ['program_name', 'description', 'genre', 'age_rating','creator']
        labels = {
            'program_name': '',
            'description': '',
            'genre': '',
            'age_rating': '',
            'creator': '',  # Added this
        }
        widgets = {
            'program_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Program Name'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'age_rating': forms.Select(attrs={'class': 'form-control'}),
            'creator': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Creator'}),  # Added this
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProgramForm, self).__init__(*args, **kwargs)
        if user:
            print('User:', user)
            # Filter creators by the current user
            self.fields['creator'].queryset = Creator.objects.filter(created_by=user)
            # Set default to the first creator
            creators = self.fields['creator'].queryset
            if creators.exists():
                self.fields['creator'].initial = creators.first()
            else:
                print('No creators found')


class EpisodeForm(ModelForm):
    class Meta:
        model = Episode
        fields = ['program', 'episode_number', 'title', 'description', 'repeat_preferences', 'start_date', 'end_date']
        labels = {
            'program': '',
            'episode_number': '',
            'title': '',
            'description': '',
            'repeat_preferences': '',
            'start_date': '',
            'end_date': '',
        }
        widgets = {
            'program': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Program'}),
            'episode_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Episode Number'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'repeat_preferences': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Repeat Preferences'}),
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
        fields = ['program', 'episode_number', 'title', 'description', 'repeat_preferences', 'start_date', 'end_date']
        labels = {
            'program': '',
            'episode_number': '',
            'title': '',
            'description': '',
            'repeat_preferences': '',
            'start_date': '',
            'end_date': '',
        }
        widgets = {
            'program': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Program'}),
            'episode_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Episode Number'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'repeat_preferences': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Repeat Preferences'}),
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
            'description': forms.Textarea(),
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

