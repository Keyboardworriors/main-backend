# Generated by Django 5.1.7 on 2025-03-25 06:02

import uuid

import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Music",
            fields=[
                (
                    "music_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                (
                    "video_id",
                    models.CharField(default="", max_length=50, unique=True),
                ),
                ("title", models.CharField(max_length=100)),
                ("artist", models.CharField(max_length=100)),
                ("thumbnail", models.URLField()),
                (
                    "embedUrl",
                    models.URLField(default="https://www.youtube.com"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Diary",
            fields=[
                (
                    "diary_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("diary_title", models.CharField(max_length=100)),
                ("content", models.TextField()),
                (
                    "moods",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=20),
                        default=list,
                        size=None,
                    ),
                ),
                ("rec_music", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="diaries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
