# Generated by Django 5.1.3 on 2024-11-23 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ch24app", "0019_program_time_slots_requested"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="creator",
            name="company",
        ),
        migrations.AddField(
            model_name="creator",
            name="channel_name",
            field=models.CharField(
                blank=True, max_length=200, verbose_name="Channel Name"
            ),
        ),
    ]
