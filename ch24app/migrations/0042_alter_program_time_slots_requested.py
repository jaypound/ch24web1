# Generated by Django 4.2.20 on 2025-04-05 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0041_alter_program_time_slots_requested'),
    ]

    operations = [
        migrations.AlterField(
            model_name='program',
            name='time_slots_requested',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
