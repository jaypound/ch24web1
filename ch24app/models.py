from django.db import models, transaction
from django.contrib.auth.models import User
import uuid
# from django.contrib.postgres.fields import JSONField
import json
from django.contrib.postgres.fields import ArrayField
from datetime import datetime
# models.pyß

TIME_SLOTS_CHOICES = [
    ('overnight', 'Overnight (2 AM - 6 AM)'),
    ('early_morning', 'Early Morning (6 AM - 9 AM)'),
    ('daytime', 'Daytime (9 AM - 3 PM)'),
    ('after_school', 'After School (3 PM - 6 PM)'),
    ('early_evening', 'Early Evening (6 PM - 8 PM)'),
    ('prime_time', 'Prime Time (8 PM - 11 PM)'),
    ('late_night', 'Late Night (11 PM - 2 AM)'),
]

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


# Create your models here.class Creator()
class Creator(models.Model):
    custom_id = models.CharField(
        max_length=36, 
        primary_key=True,
        default=uuid.uuid4,  # Generates a unique UUID for each instance
        editable=False)
    first_name = models.CharField('First Name', max_length=100)
    last_name = models.CharField('Last Name', max_length=100)
    channel_name = models.CharField('Channel Name', blank=True, max_length=200, unique=True)  # Ensure channel_name is unique
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
        return f"{self.channel_name}"
        # return f"{self.first_name} {self.last_name}"


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
    time_slots_requested = models.CharField(
        'Time Slots Requested',
        max_length=255,
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
    start_date = models.DateField('Start Date', null=True, blank=True)
    end_date = models.DateField('End Date', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.TextField('File Name', blank=True)
    has_mediainfo_errors = models.BooleanField(default=False, db_index=True) 
    transcription = models.TextField('Transcription', blank=True)
    ai_summary = models.TextField('AI Summary', blank=True)
    ai_genre = models.CharField(
        'AI Generated Genre',
        max_length=50,
        choices=GENRE_CHOICES,
        blank=True
    )
    ai_age_rating = models.CharField(
        'AI Generated Age Rating',
        max_length=10,
        choices=AGE_RATING_CHOICES,
        blank=True
    )
    ai_topics = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    ai_time_slots_recommended = models.CharField(
        'Time Slots Requested',
        max_length=255,
        blank=True
    )
    audience_engagement_score = models.IntegerField('Audience Engagement Score', blank=True, null=True)
    audience_engagement_reasons = models.TextField('Audience Engagement Reasons', blank=True)
    prohibited_content = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        null=True,
        default=list
    )
    prohibited_content_reasons = models.TextField('Prohibited Content Reasons', blank=True, null=True)
    ready_for_air = models.BooleanField(
        'Ready for Air',
        default=True,
        db_index=True,
        help_text='Indicates whether this content is ready for scheduling.'
    )
    last_timeslot = models.CharField('Last Time Slot', max_length=50, blank=True, null=True)
    last_scheduled = models.DateTimeField('Last Scheduled Time', blank=True, null=True)
    schedule_count = models.IntegerField('Schedule Count', default=0, blank=True, null=True)
    priority_score = models.IntegerField('Priority Score', default=0, blank=True, null=True)
    duration_seconds = models.IntegerField('Duration in Seconds', blank=True, null=True)
    duration_timecode = models.CharField('Duration Timecode', max_length=20, blank=True, null=True)

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
    
    from django.db import models
from django.forms import ValidationError
from django.utils import timezone

# Assuming you have an Episode model already defined as follows:
# class Episode(models.Model):
#     custom_id = models.CharField(max_length=36, primary_key=True, ...)

class EpisodeProcessingJob(models.Model):
    # A foreign key to the Episode model, assuming 'custom_id' is the primary key field of the Episode model
    episode = models.ForeignKey('Episode', on_delete=models.CASCADE, to_field='custom_id')
    
    file_name = models.CharField(max_length=255)
    start_time = models.DateTimeField(default=timezone.now)
    stop_time = models.DateTimeField(null=True, blank=True)
    
    # You can use choices to define a set of fixed values for completion status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    completion_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    aws_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    errors = models.TextField(blank=True)

    def __str__(self):
        return f"Processing Job for {self.episode.custom_id}"


class ScheduledEpisode(models.Model):
    custom_id = models.CharField(
        max_length=36, 
        primary_key=True,
        default=uuid.uuid4,  # Generates a unique UUID for each instance
        editable=False)
    schedule_date = models.DateField(
        'Schedule Date',
        db_index=True,  # Add index for better query performance
        help_text='Date this episode is scheduled to air',
        null=True,  # Explicitly disallow NULL values
        blank=True  # Required in forms
    )
    start_time = models.DateTimeField(blank=True, null=True, verbose_name='Start Time')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='End Time')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    episode_number = models.IntegerField('Episode Number')
    title = models.CharField('Title', max_length=255)
    file_name = models.TextField('File Name', blank=True)
    ai_genre = models.CharField(
        'AI Generated Genre',
        max_length=50,
        choices=GENRE_CHOICES,
        blank=True
    )
    ai_age_rating = models.CharField(
        'AI Generated Age Rating',
        max_length=10,
        choices=AGE_RATING_CHOICES,
        blank=True
    )
    ai_topics = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    ai_time_slots_recommended = models.CharField(
        'Time Slots Requested',
        max_length=255,
        blank=True
    )
    audience_engagement_score = models.IntegerField('Audience Engagement Score', blank=True, null=True)
    audience_engagement_reasons = models.TextField('Audience Engagement Reasons', blank=True)
    prohibited_content = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        null=True,
        default=list
    )
    prohibited_content_reasons = models.TextField('Prohibited Content Reasons', blank=True, null=True)
    ready_for_air = models.BooleanField(
        'Ready for Air',
        default=True,
        db_index=True,
        help_text='Indicates whether this content is ready for scheduling.'
    )
    last_timeslot = models.CharField('Last Time Slot', max_length=50, blank=True, null=True)
    last_scheduled = models.DateTimeField('Last Scheduled Time', blank=True, null=True)
    schedule_count = models.IntegerField('Schedule Count', default=0, blank=True, null=True)
    duration_seconds = models.IntegerField('Duration in Seconds', blank=True, null=True)
    duration_timecode = models.CharField('Duration Timecode', max_length=20, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['schedule_date', 'start_time']),
            models.Index(fields=['creator', 'schedule_date']),
            models.Index(fields=['ai_genre', 'ai_age_rating']),
            models.Index(fields=['duration_seconds']),
            models.Index(fields=['ready_for_air', 'ai_age_rating'])
        ]
        ordering = ['schedule_date', 'start_time']  # Default ordering

        # constraints = [
        #     models.CheckConstraint(
        #         check=Q(end_time__gt=models.F('start_time')),
        #         name='end_time_after_start_time'
        #     ),
        #     models.CheckConstraint(
        #         check=Q(duration_seconds__gt=0),
        #         name='positive_duration'
        #     ),
        #     models.UniqueConstraint(
        #     fields=['schedule_date', 'start_time', 'creator'],
        #     name='unique_timeslot_per_creator'
        # ),
        # ]

    def __str__(self):
        return f"{self.schedule_date} - {self.start_time}: {self.title}"
    
    
    def get_datetime_start(self):
        """Get combined datetime for schedule_date and start_time"""
        return datetime.combine(self.schedule_date, self.start_time)

    def get_datetime_end(self):
        """Get combined datetime for schedule_date and end_time"""
        return datetime.combine(self.schedule_date, self.end_time)

    def overlaps_with(self, other):
        """Check if this scheduled episode overlaps with another"""
        if self.schedule_date != other.schedule_date:
            return False
        return (self.start_time < other.end_time and 
                self.end_time > other.start_time)
    
    def clean(self):
        """Validate the model"""
        super().clean()
        if self.start_time and self.end_time:
        # Verify times are within same day
            if self.end_time < self.start_time:
                raise ValidationError({
                    'end_time': 'End time must be after start time'
                })
        
        # Calculate duration matches duration_seconds
        start_dt = self.get_datetime_start()
        end_dt = self.get_datetime_end()
        duration = (end_dt - start_dt).total_seconds()
        if duration != self.duration_seconds:
            raise ValidationError(
                'Duration mismatch between times and duration_seconds'
            )

        # Check for overlaps
        overlapping = ScheduledEpisode.objects.filter(
            schedule_date=self.schedule_date,
            creator=self.creator
        ).exclude(pk=self.pk)
        for other in overlapping:
            if self.overlaps_with(other):
                raise ValidationError(
                    'This timeslot overlaps with another scheduled episode'
                )