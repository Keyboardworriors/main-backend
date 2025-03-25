from django.contrib import admin

from .models import Diary, Music


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ("music_id", "title", "artist", "video_id", "thumbnail")
    search_fields = ("title", "artist", "video_id")
    readonly_fields = ("music_id",)


@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    list_display = ("diary_id", "diary_title", "member", "created_at")
    search_fields = ("diary_title", "content", "member__email")
    list_filter = ("moods",)
    readonly_fields = ("diary_id", "created_at")
