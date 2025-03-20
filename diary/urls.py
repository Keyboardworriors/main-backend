from django.urls import path

from diary.views import (
    DiaryCreateView,
    DiaryDetailView,
    DiaryListView,
    DiarySearchView,
)

app_name = "diary"
urlpatterns = [
    path("", DiaryListView.as_view(), name="diary-main"),
    path("<uuid:diary_id>/", DiaryDetailView.as_view(), name="diary-detail"),
    path("search/", DiarySearchView.as_view(), name="diary-search"),
    path("create/", DiaryCreateView.as_view(), name="diary-create"),

]
