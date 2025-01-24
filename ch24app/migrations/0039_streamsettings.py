# Generated by Django 4.2.17 on 2025-01-24 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0038_homemessage_alter_episode_ai_genre_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_stream_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Stream Settings',
                'verbose_name_plural': 'Stream Settings',
            },
        ),
    ]
