from django.db import models
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
    

# class Program(models.Model):
#     custom_id = models.CharField(
#         max_length=36, 
#         primary_key=True,
#         default=uuid.uuid4,  # Generates a unique UUID for each instance
#         editable=False)
#     creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
#     program_name = models.CharField('Program Name', max_length=255)
#     description = models.TextField('Description', blank=True)
#     genre = models.CharField('Genre (e.g.News, Comedy, Talk Show)', max_length=255, blank=True)
#     age_rating = models.CharField('Age Rating (e.g. TV-14, TV-MA)', max_length=255, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)

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

    def save(self, *args, **kwargs):
        # Assign a unique ID if not already set
        if not self.custom_id:
            self.custom_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.program.program_name} - Episode {self.episode_number}: {self.title}"
    
# class MediaInfo(models.Model):
#     episode = models.ForeignKey('Episode', on_delete=models.CASCADE, related_name='media_infos')
#     track_id = models.IntegerField()
#     metadata = models.JSONField()  # Use JSONField if supported

    # def __str__(self):
    #     return f"MediaInfo for {self.episode.custom_id}, Track {self.track_id}"
    
    # If JSONField is not supported, use this method to handle JSON serialization
    # metadata = models.TextField()

    # def save(self, *args, **kwargs):
    #     self.metadata = json.dumps(self.metadata)
    #     super().save(*args, **kwargs)

    # def get_metadata(self):
    #     return json.loads(self.metadata)


class EpisodeMediaInfo(models.Model):
    episode = models.ForeignKey('Episode', on_delete=models.CASCADE, related_name='media_infos')
    track_id = models.IntegerField()
    metadata = models.JSONField()  # Use JSONField if supported

    def __str__(self):
        return f"MediaInfo for {self.episode.custom_id}, Track {self.track_id}"
