# Generated by Django 4.2.17 on 2024-12-07 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0028_alter_episode_last_timeslot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='schedule_count',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Schedule Count'),
        ),
    ]
