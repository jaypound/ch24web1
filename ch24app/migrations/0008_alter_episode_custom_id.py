# Generated by Django 5.1.2 on 2024-11-02 17:02

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ch24app', '0007_episode_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='custom_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
