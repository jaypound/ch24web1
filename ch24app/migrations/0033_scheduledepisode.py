# Generated by Django 4.2.17 on 2024-12-26 17:41

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0032_episode_duration_seconds_episode_duration_timecode'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduledEpisode',
            fields=[
                ('custom_id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('episode_number', models.IntegerField(verbose_name='Episode Number')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('file_name', models.TextField(blank=True, verbose_name='File Name')),
                ('ai_genre', models.CharField(blank=True, choices=[('News/Weather Report', 'News/Weather Report'), ('News Magazine', 'News Magazine'), ('Documentary', 'Documentary'), ('Discussion/Interview/Debate', 'Discussion/Interview/Debate'), ('Talk Show', 'Talk Show'), ('Performing Arts', 'Performing Arts'), ('Fine Arts', 'Fine Arts'), ('Religion', 'Religion'), ('Popular Culture/Traditional Arts', 'Popular Culture/Traditional Arts'), ('Rock/Pop', 'Rock/Pop'), ('Folk/Traditional Music', 'Folk/Traditional Music'), ('Sports Magazine', 'Sports Magazine'), ('Team Sports', 'Team Sports'), ('Entertainment Programmes for 6-14', 'Entertainment Programmes for 6-14'), ('Informational/Educational/School Programmes', 'Informational/Educational/School Programmes'), ('Nature/Animals/Environment', 'Nature/Animals/Environment'), ('Technology/Natural Sciences', 'Technology/Natural Sciences'), ('Medicine/Physiology/Psychology', 'Medicine/Physiology/Psychology'), ('Magazines/Reports/Documentary', 'Magazines/Reports/Documentary'), ('Economics/Social Advisory', 'Economics/Social Advisory'), ('Tourism/Travel', 'Tourism/Travel'), ('Handicraft', 'Handicraft'), ('Fitness and Health', 'Fitness and Health'), ('Cooking', 'Cooking')], max_length=50, verbose_name='AI Generated Genre')),
                ('ai_age_rating', models.CharField(blank=True, choices=[('TV-Y', 'TV-Y: All Children'), ('TV-Y7', 'TV-Y7: Directed to Older Children'), ('TV-G', 'TV-G: General Audience'), ('TV-PG', 'TV-PG: Parental Guidance Suggested'), ('TV-14', 'TV-14: Parents Strongly Cautioned'), ('TV-MA', 'TV-MA: Mature Audience Only')], max_length=10, verbose_name='AI Generated Age Rating')),
                ('ai_topics', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None)),
                ('ai_time_slots_recommended', models.CharField(blank=True, max_length=255, verbose_name='Time Slots Requested')),
                ('audience_engagement_score', models.IntegerField(blank=True, null=True, verbose_name='Audience Engagement Score')),
                ('audience_engagement_reasons', models.TextField(blank=True, verbose_name='Audience Engagement Reasons')),
                ('prohibited_content', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, null=True, size=None)),
                ('prohibited_content_reasons', models.TextField(blank=True, null=True, verbose_name='Prohibited Content Reasons')),
                ('ready_for_air', models.BooleanField(db_index=True, default=True, help_text='Indicates whether this content is ready for scheduling.', verbose_name='Ready for Air')),
                ('last_timeslot', models.CharField(blank=True, max_length=50, null=True, verbose_name='Last Time Slot')),
                ('last_scheduled', models.DateTimeField(blank=True, null=True, verbose_name='Last Scheduled Time')),
                ('schedule_count', models.IntegerField(blank=True, default=0, null=True, verbose_name='Schedule Count')),
                ('duration_seconds', models.IntegerField(blank=True, null=True, verbose_name='Duration in Seconds')),
                ('duration_timecode', models.CharField(blank=True, max_length=20, null=True, verbose_name='Duration Timecode')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ch24app.creator')),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ch24app.episode')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ch24app.program')),
            ],
        ),
    ]
