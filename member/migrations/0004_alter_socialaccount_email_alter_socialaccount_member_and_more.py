# Generated by Django 5.1.7 on 2025-03-17 03:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("member", "0003_member_groups_member_is_active_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="socialaccount",
            name="email",
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name="socialaccount",
            name="member",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="social_accounts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="socialaccount",
            name="provider_user_id",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name="socialaccount",
            unique_together={("provider", "email")},
        ),
    ]
