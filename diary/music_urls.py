from django.urls import path

from diary.views_music import MusicRedommendView

app_name = "music"

urlpatterns = [
    path("recommend", MusicRedommendView.as_view(), name="music-recommend")
]
