# Generated by Django 5.1.7 on 2025-03-19 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("diary", "0002_alter_diary_diary_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="diary",
            old_name="member_id",
            new_name="member",
        ),
    ]
