from django.urls import path

from diary.views import DiarySearchAPIView, DiaryList, DiaryDetail, DiaryCreateAPIView, DiaryCustomDateCreateAPIView

app_name = "diary"
urlpatterns = [
    path("api/diary/", DiaryList.as_view(), name="diary-main"),
    path("api/diary/<int:diary_id>/", DiaryDetail.as_view(), name="diary-detail"),
    path(
        "api/diary/search/", DiarySearchAPIView.as_view(), name="diary-search"
    ),
    path("api/diary/create/", DiaryCreateAPIView.as_view(), name="diary-create"),
    path("api/diary/custom-date/",DiaryCustomDateCreateAPIView.as_view(), name="diary-custom-date"),
]
