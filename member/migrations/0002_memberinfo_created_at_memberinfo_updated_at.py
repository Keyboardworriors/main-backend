# Generated by Django 5.1.7 on 2025-03-23 17:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("member", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberinfo",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="memberinfo",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
