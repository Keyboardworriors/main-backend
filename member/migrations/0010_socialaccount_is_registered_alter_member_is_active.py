# Generated by Django 5.1.7 on 2025-03-19 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("member", "0009_alter_member_nickname"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialaccount",
            name="is_registered",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="member",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
