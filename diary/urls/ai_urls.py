from django.urls.conf import path

from diary.views.ai_views import GetMoods

app_name = "ai"

urlpatterns = [
    path("", GetMoods.as_view(), name="get_emotions"),
]
