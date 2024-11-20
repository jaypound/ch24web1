# Generated by Django 5.1.3 on 2024-11-19 20:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0013_alter_program_age_rating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_no', models.IntegerField(editable=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('contact_info', models.EmailField(max_length=254)),
                ('category', models.CharField(choices=[('account', 'Account and Login Issues'), ('registration', 'Program and Episode Registration'), ('uploads', 'Content Uploads'), ('playback', 'Playback and Scheduling'), ('technical', 'Technical Issues'), ('policy', 'Policy and Guidelines'), ('feedback', 'Feedback and Suggestions'), ('other', 'Other')], max_length=50)),
                ('subject', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('time_received', models.DateTimeField(auto_now_add=True)),
                ('urgency', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], max_length=10)),
                ('ticket_status', models.CharField(choices=[('SUBMITTED', 'Submitted'), ('WORKING', 'Working'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed'), ('PENDING', 'Pending'), ('ON_HOLD', 'On Hold')], default='SUBMITTED', max_length=20)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ch24app.creator')),
                ('episode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ch24app.episode')),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ch24app.program')),
            ],
        ),
        migrations.CreateModel(
            name='TicketResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_no', models.IntegerField(editable=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
                ('responder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='ch24app.supportticket')),
            ],
        ),
    ]
