from django.urls import path

from diary.views_music import MusicRecommendationView

app_name = "music"

urlpatterns = [
    path("recommend", MusicRecommendationView.as_view(), name="music-recommend")
]
