# Generated by Django 4.2.17 on 2024-12-07 16:09

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0026_remove_episode_ai_age_rating_remove_episode_ai_genre_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('custom_id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('transcription', models.TextField(blank=True, verbose_name='Transcription')),
                ('ai_summary', models.TextField(blank=True, verbose_name='AI Summary')),
                ('ai_genre', models.CharField(blank=True, choices=[('News/Weather Report', 'News/Weather Report'), ('News Magazine', 'News Magazine'), ('Documentary', 'Documentary'), ('Discussion/Interview/Debate', 'Discussion/Interview/Debate'), ('Talk Show', 'Talk Show'), ('Performing Arts', 'Performing Arts'), ('Fine Arts', 'Fine Arts'), ('Religion', 'Religion'), ('Popular Culture/Traditional Arts', 'Popular Culture/Traditional Arts'), ('Rock/Pop', 'Rock/Pop'), ('Folk/Traditional Music', 'Folk/Traditional Music'), ('Sports Magazine', 'Sports Magazine'), ('Team Sports', 'Team Sports'), ('Entertainment Programmes for 6-14', 'Entertainment Programmes for 6-14'), ('Informational/Educational/School Programmes', 'Informational/Educational/School Programmes'), ('Nature/Animals/Environment', 'Nature/Animals/Environment'), ('Technology/Natural Sciences', 'Technology/Natural Sciences'), ('Medicine/Physiology/Psychology', 'Medicine/Physiology/Psychology'), ('Magazines/Reports/Documentary', 'Magazines/Reports/Documentary'), ('Economics/Social Advisory', 'Economics/Social Advisory'), ('Tourism/Travel', 'Tourism/Travel'), ('Handicraft', 'Handicraft'), ('Fitness and Health', 'Fitness and Health'), ('Cooking', 'Cooking')], max_length=50, verbose_name='AI Generated Genre')),
                ('ai_age_rating', models.CharField(blank=True, choices=[('TV-Y', 'TV-Y: All Children'), ('TV-Y7', 'TV-Y7: Directed to Older Children'), ('TV-G', 'TV-G: General Audience'), ('TV-PG', 'TV-PG: Parental Guidance Suggested'), ('TV-14', 'TV-14: Parents Strongly Cautioned'), ('TV-MA', 'TV-MA: Mature Audience Only')], max_length=10, verbose_name='AI Generated Age Rating')),
                ('ai_topics', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None)),
                ('ai_time_slots_recommended', models.CharField(blank=True, max_length=255, verbose_name='Time Slots Requested')),
                ('audience_engagement_score', models.IntegerField(blank=True, null=True, verbose_name='Audience Engagement Score')),
                ('audience_engagement_reasons', models.TextField(blank=True, verbose_name='Audience Engagement Reasons')),
                ('use_analysis', models.BooleanField(default=True, help_text='Indicates whether this analysis should be considered when scheduling.', verbose_name='Use This Analysis')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='episode',
            name='last_scheduled',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Last Scheduled Time'),
        ),
        migrations.AddField(
            model_name='episode',
            name='last_timeslot',
            field=models.CharField(blank=True, max_length=50, verbose_name='Last Time Slot'),
        ),
        migrations.AddField(
            model_name='episode',
            name='schedule_count',
            field=models.IntegerField(default=0, verbose_name='Schedule Count'),
        ),
        migrations.DeleteModel(
            name='Transcription',
        ),
        migrations.AddField(
            model_name='analysis',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analyses', to='ch24app.episode'),
        ),
    ]
