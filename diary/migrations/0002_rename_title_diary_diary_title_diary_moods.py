# Generated by Django 5.1.7 on 2025-03-18 05:56

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("diary", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="diary",
            old_name="title",
            new_name="diary_title",
        ),
        migrations.AddField(
            model_name="diary",
            name="moods",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=20),
                default=list,
                size=None,
            ),
        ),
    ]
