from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from config import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("members/", include("member.urls")),
    path("diarys/", include("diary.urls")),
    path("diarys/ai/", include("diary.ai_urls")),
    path("diarys/music/", include("diary.music_urls")),

]
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]