from django.db import models, transaction
from django.contrib.auth.models import User
import uuid
# from django.contrib.postgres.fields import JSONField
import json

AGE_RATING_CHOICES = [
    ('TV-Y', 'TV-Y: All Children'),
    ('TV-Y7', 'TV-Y7: Directed to Older Children'),
    ('TV-G', 'TV-G: General Audience'),
    ('TV-PG', 'TV-PG: Parental Guidance Suggested'),
    ('TV-14', 'TV-14: Parents Strongly Cautioned'),
    ('TV-MA', 'TV-MA: Mature Audience Only'),
]

GENRE_CHOICES = [
    ('News/Weather Report', 'News/Weather Report'),
    ('News Magazine', 'News Magazine'),
    ('Documentary', 'Documentary'),
    ('Discussion/Interview/Debate', 'Discussion/Interview/Debate'),
    ('Talk Show', 'Talk Show'),
    ('Performing Arts', 'Performing Arts'),
    ('Fine Arts', 'Fine Arts'),
    ('Religion', 'Religion'),
    ('Popular Culture/Traditional Arts', 'Popular Culture/Traditional Arts'),
    ('Rock/Pop', 'Rock/Pop'),
    ('Folk/Traditional Music', 'Folk/Traditional Music'),
    ('Sports Magazine', 'Sports Magazine'),
    ('Team Sports', 'Team Sports'),
    ('Entertainment Programmes for 6-14', 'Entertainment Programmes for 6-14'),
    ('Informational/Educational/School Programmes', 'Informational/Educational/School Programmes'),
    ('Nature/Animals/Environment', 'Nature/Animals/Environment'),
    ('Technology/Natural Sciences', 'Technology/Natural Sciences'),
    ('Medicine/Physiology/Psychology', 'Medicine/Physiology/Psychology'),
    ('Magazines/Reports/Documentary', 'Magazines/Reports/Documentary'),
    ('Economics/Social Advisory', 'Economics/Social Advisory'),
    ('Tourism/Travel', 'Tourism/Travel'),
    ('Handicraft', 'Handicraft'),
    ('Fitness and Health', 'Fitness and Health'),
    ('Cooking', 'Cooking'),
]

REPEAT_CHOICES = [
    ('once', 'Once'),
    ('weekly', 'Weekly'),
    ('specific', 'Specific Day / Time Slot'),
]

# Create your models here.class Creator()
class Creator(models.Model):
    custom_id = models.CharField(
        max_length=36, 
        primary_key=True,
        default=uuid.uuid4,  # Generates a unique UUID for each instance
        editable=False)
    first_name = models.CharField('First Name', max_length=100)
    last_name = models.CharField('Last Name', max_length=100)
    company = models.CharField('Company', blank=True, max_length=200)
    address = models.CharField('Address', blank=True, max_length=255)
    city = models.CharField('City', blank=True, max_length=255)
    state = models.CharField('State', blank=True, max_length=255)
    zip_code = models.CharField('Zip Code', blank=True, max_length=16)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Phone', blank=True, max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Assign a unique ID if not already set
        if not self.custom_id:
            self.custom_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
# from django.db import models
# from django.contrib.auth.models import User
# import uuid

# class Creator(models.Model):
#     custom_id = models.UUIDField(
#         primary_key=True,
#         default=uuid.uuid4,
#         editable=False
#     )
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='creator_profile')
#     first_name = models.CharField('First Name', max_length=100)
#     last_name = models.CharField('Last Name', max_length=100)
#     company = models.CharField('Company', blank=True, max_length=200)
#     address = models.CharField('Address', blank=True, max_length=255)
#     city = models.CharField('City', blank=True, max_length=255)
#     state = models.CharField('State', blank=True, max_length=255)
#     zip_code = models.CharField('Zip Code', blank=True, max_length=16)
#     email = models.EmailField('Email', unique=True)
#     phone = models.CharField('Phone', blank=True, max_length=25)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"


class Program(models.Model):
    custom_id = models.CharField(
        max_length=36,
        primary_key=True,
        default=uuid.uuid4,  # Generates a unique UUID for each instance
        editable=False
    )
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE)
    program_name = models.CharField('Program Name', max_length=255)
    description = models.TextField('Description', blank=True)
    genre = models.CharField(
        'Genre',
        max_length=50,  # Adjusted to accommodate the longest genre name
        choices=GENRE_CHOICES,
        blank=True
    )
    age_rating = models.CharField(
        'Age Rating',
        max_length=10,
        choices=AGE_RATING_CHOICES,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Assign a unique ID if not already set
        if not self.custom_id:
            self.custom_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.program_name
    

class Episode(models.Model):
    custom_id = models.CharField(
        max_length=36, 
        primary_key=True,
        default=uuid.uuid4,  # Generates a unique UUID for each instance
        editable=False)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    episode_number = models.IntegerField('Episode Number')
    title = models.CharField('Title', max_length=255)
    description = models.TextField('Description', blank=True)
    repeat_preferences = models.CharField('Repeat Preferences (e.g. daily, weekly, or specific day/time)', max_length=255, blank=True)
    start_date = models.DateField('Start Date', null=True, blank=True)
    end_date = models.DateField('End Date', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.TextField('File Name', blank=True)
    has_mediainfo_errors = models.BooleanField(default=False, db_index=True)

    def save(self, *args, **kwargs):
        # Assign a unique ID if not already set
        if not self.custom_id:
            self.custom_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.program.program_name} - Episode {self.episode_number}: {self.title}"


class EpisodeMediaInfo(models.Model):
    episode = models.ForeignKey('Episode', on_delete=models.CASCADE, related_name='media_infos')
    track_id = models.IntegerField()
    metadata = models.JSONField()  # Use JSONField if supported

    def __str__(self):
        return f"MediaInfo for {self.episode.custom_id}, Track {self.track_id}"


class SupportTicket(models.Model):
    TICKET_CATEGORIES = [
        ('account', 'Account and Login Issues'),
        ('registration', 'Program and Episode Registration'),
        ('uploads', 'Content Uploads'),
        ('playback', 'Playback and Scheduling'),
        ('technical', 'Technical Issues'),
        ('policy', 'Policy and Guidelines'),
        ('feedback', 'Feedback and Suggestions'),
        ('other', 'Other'),
    ]

    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('WORKING', 'Working'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
        ('PENDING', 'Pending'),
        ('ON_HOLD', 'On Hold'),
    ]

    ticket_no = models.IntegerField(unique=True, editable=False)
    name = models.CharField(max_length=100)
    contact_info = models.EmailField()
    category = models.CharField(max_length=50, choices=TICKET_CATEGORIES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    time_received = models.DateTimeField(auto_now_add=True)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    ticket_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUBMITTED',
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    creator = models.ForeignKey('Creator', on_delete=models.SET_NULL, null=True, blank=True)
    program = models.ForeignKey('Program', on_delete=models.SET_NULL, null=True, blank=True)
    episode = models.ForeignKey('Episode', on_delete=models.SET_NULL, null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.ticket_no:
            with transaction.atomic():
                last_ticket = SupportTicket.objects.select_for_update().order_by('-ticket_no').first()
                self.ticket_no = last_ticket.ticket_no + 1 if last_ticket else 1
        super(SupportTicket, self).save(*args, **kwargs)

    def __str__(self):
        return f"Ticket #{self.ticket_no} - {self.subject}"


class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, related_name='responses', on_delete=models.CASCADE)
    response_no = models.IntegerField(editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()

    def save(self, *args, **kwargs):
        if not self.response_no:
            with transaction.atomic():
                last_response = TicketResponse.objects.filter(ticket=self.ticket).select_for_update().order_by('-response_no').first()
                self.response_no = last_response.response_no + 1 if last_response else 1
        super(TicketResponse, self).save(*args, **kwargs)

    def __str__(self):
        return f"Response #{self.response_no} to Ticket #{self.ticket.ticket_no}"