# Generated by Django 4.2.17 on 2024-12-23 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0031_episode_ai_age_rating_episode_ai_genre_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='duration_seconds',
            field=models.IntegerField(blank=True, null=True, verbose_name='Duration in Seconds'),
        ),
        migrations.AddField(
            model_name='episode',
            name='duration_timecode',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Duration Timecode'),
        ),
    ]
