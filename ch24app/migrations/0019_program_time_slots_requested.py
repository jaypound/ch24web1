# Generated by Django 5.1.3 on 2024-11-22 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ch24app", "0018_alter_episode_has_mediainfo_errors"),
    ]

    operations = [
        migrations.AddField(
            model_name="program",
            name="time_slots_requested",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="Time Slots Requested"
            ),
        ),
    ]