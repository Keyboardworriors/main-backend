from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from config import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/members/", include("member.urls")),
    path("oauth/", include("member.oauth_urls")),
    path("api/diary/", include("diary.urls")),
    path("api/diary/ai/", include("diary.ai_urls")),
    path("api/diary/music/", include("diary.music_urls")),
]
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
