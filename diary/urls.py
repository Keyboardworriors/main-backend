from django.urls import path

from diary.views import (
    DiaryCreateAPIView,
    DiaryCustomDateCreateAPIView,
    DiaryDetail,
    DiaryList,
    DiarySearchAPIView,
)

app_name = "diary"
urlpatterns = [
    path("", DiaryList.as_view(), name="diary-main"),
    path("<int:diary_id>/", DiaryDetail.as_view(), name="diary-detail"),
    path("search/", DiarySearchAPIView.as_view(), name="diary-search"),
    path("create/", DiaryCreateAPIView.as_view(), name="diary-create"),
    path(
        "custom-date/",
        DiaryCustomDateCreateAPIView.as_view(),
        name="diary-custom-date",
    ),
]
