# Generated by Django 4.2.17 on 2024-12-26 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0033_scheduledepisode'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scheduledepisode',
            options={'ordering': ['schedule_date', 'start_time']},
        ),
        migrations.AddField(
            model_name='scheduledepisode',
            name='end_time',
            field=models.TimeField(blank=True, null=True, verbose_name='End Time'),
        ),
        migrations.AddField(
            model_name='scheduledepisode',
            name='schedule_date',
            field=models.DateField(blank=True, db_index=True, help_text='Date this episode is scheduled to air', null=True, verbose_name='Schedule Date'),
        ),
        migrations.AddField(
            model_name='scheduledepisode',
            name='start_time',
            field=models.TimeField(blank=True, null=True, verbose_name='Start Time'),
        ),
        migrations.AddIndex(
            model_name='scheduledepisode',
            index=models.Index(fields=['schedule_date', 'start_time'], name='ch24app_sch_schedul_d1a045_idx'),
        ),
        migrations.AddIndex(
            model_name='scheduledepisode',
            index=models.Index(fields=['creator', 'schedule_date'], name='ch24app_sch_creator_fbcb9c_idx'),
        ),
        migrations.AddIndex(
            model_name='scheduledepisode',
            index=models.Index(fields=['ai_genre', 'ai_age_rating'], name='ch24app_sch_ai_genr_505889_idx'),
        ),
        migrations.AddIndex(
            model_name='scheduledepisode',
            index=models.Index(fields=['duration_seconds'], name='ch24app_sch_duratio_16b93f_idx'),
        ),
        migrations.AddIndex(
            model_name='scheduledepisode',
            index=models.Index(fields=['ready_for_air', 'ai_age_rating'], name='ch24app_sch_ready_f_fd5aa5_idx'),
        ),
    ]