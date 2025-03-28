import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField
from django.utils import timezone


def get_today_date():
    return timezone.now().date()


# 다이어리 테이블
class Diary(models.Model):
    diary_id = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False
    )
    member = models.ForeignKey(
        "member.SocialAccount", on_delete=models.CASCADE, related_name="diaries"
    )
    diary_title = models.CharField(max_length=100)
    content = models.TextField()
    moods = ArrayField(models.CharField(max_length=20), default=list)
    rec_music = JSONField(blank=True, null=True)
    date = models.DateField(default=get_today_date)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.diary_title
