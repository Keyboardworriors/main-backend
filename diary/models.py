from django.db import models


# 음악정보 저장 테이블
class Music(models.Model):
    music_id = models.UUIDField(primary_key=True, unique=True)
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title


# 다이어리 테이블
class Diary(models.Model):
    diary_id = models.UUIDField(primary_key=True, unique=True)
    member_id = models.ForeignKey(
        "member.Member", on_delete=models.CASCADE, related_name="diaries"
    )
    diary_title = models.CharField(max_length=100)
    content = models.TextField()
    moods = models.JSONField(default=list)
    rec_music = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.diary_title
