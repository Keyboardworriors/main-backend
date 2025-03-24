from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/members/", include("member.urls.api_urls")),
    path("api/oauth/", include("member.urls.oauth_urls")),
    path("api/diary/", include("diary.urls")),
    path("api/diary/recommendation-keyword", include("diary.ai_urls")),
    path("api/diary/music/", include("diary.music_urls")),
]
