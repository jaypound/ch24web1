# Generated by Django 5.1.2 on 2024-10-26 20:21

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Creator',
            fields=[
                ('custom_id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=255, verbose_name='Last Name')),
                ('company', models.CharField(blank=True, max_length=255, verbose_name='Company')),
                ('address', models.CharField(blank=True, max_length=255, verbose_name='Address')),
                ('city', models.CharField(blank=True, max_length=255, verbose_name='City')),
                ('state', models.CharField(blank=True, max_length=255, verbose_name='State')),
                ('zip_code', models.CharField(blank=True, max_length=255, verbose_name='Zip Code')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=255, verbose_name='Phone')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
