from django.urls import path

from diary.views.diary_views import (
    DiaryCreateView,
    DiaryDetailView,
    DiaryListView,
    DiarySearchView,
    EmotionStatusView,
)

app_name = "diary"
urlpatterns = [
    path("", DiaryListView.as_view(), name="diary-main"),
    path("<uuid:diary_id>/", DiaryDetailView.as_view(), name="diary-detail"),
    path("search/", DiarySearchView.as_view(), name="diary-search"),
    path("create/", DiaryCreateView.as_view(), name="diary-create"),
    path("by-period/", EmotionStatusView.as_view(), name="emotion-status"),
]
