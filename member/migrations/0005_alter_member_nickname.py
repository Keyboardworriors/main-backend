# Generated by Django 5.1.7 on 2025-03-17 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "member",
            "0004_alter_socialaccount_email_alter_socialaccount_member_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="member",
            name="nickname",
            field=models.CharField(max_length=20),
        ),
    ]
