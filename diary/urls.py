from django.urls import path

from diary.views import DiaryAPIView

app_name = "diary"
urlpatterns = [
    path("api/diary", DiaryAPIView.as_view(), name="diary_main"),
    path(
        "api/diary/<diary_id:int>", DiaryAPIView.as_view(), name="diary_detail"
    ),
    path(
        "api/diary/search/", DiarySearchAPIView.as_view(), name="diary-search"
    ),
]
