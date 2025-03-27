from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/members/", include("member.urls.api_urls")),
    path("api/oauth/", include("member.urls.oauth_urls")),
    path("api/diary/", include("diary.urls.diary_urls")),
    path("api/diary/recommendation-keyword/", include("diary.urls.ai_urls")),
    path("api/diary/music/", include("diary.urls.music_urls")),
]
