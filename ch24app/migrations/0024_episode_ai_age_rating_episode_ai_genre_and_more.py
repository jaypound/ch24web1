# Generated by Django 5.1.3 on 2024-12-03 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ch24app", "0023_episodeprocessingjob"),
    ]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="ai_age_rating",
            field=models.CharField(
                blank=True, max_length=10, verbose_name="AI Generated Age Rating"
            ),
        ),
        migrations.AddField(
            model_name="episode",
            name="ai_genre",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="AI Generated Genre"
            ),
        ),
        migrations.AddField(
            model_name="episode",
            name="ai_summary",
            field=models.TextField(blank=True, verbose_name="AI Summary"),
        ),
        migrations.AddField(
            model_name="episode",
            name="last_scheduled",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Last Scheduled Time"
            ),
        ),
        migrations.AddField(
            model_name="episode",
            name="last_timeslot",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="Last Time Slot"
            ),
        ),
        migrations.AddField(
            model_name="episode",
            name="schedule_count",
            field=models.IntegerField(default=0, verbose_name="Schedule Count"),
        ),
        migrations.AddField(
            model_name="episode",
            name="transcription",
            field=models.TextField(blank=True, verbose_name="Transcription"),
        ),
    ]
