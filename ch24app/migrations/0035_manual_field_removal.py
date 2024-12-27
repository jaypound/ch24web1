from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0034_alter_scheduledepisode_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheduledepisode',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='scheduledepisode',
            name='start_time',
        ),
        migrations.AddField(
            model_name='scheduledepisode',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scheduledepisode',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
