from django.urls import path

from diary.views_music import MusicRecommendView

app_name = "music"

urlpatterns = [
    path("recommend", MusicRecommendView.as_view(), name="music-recommend")
]
