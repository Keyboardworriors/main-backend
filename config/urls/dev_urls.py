from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from config import settings

# Swagger 문서 생성을 위한 설정
schema_view = get_schema_view(
    openapi.Info(
        title="Feelody",
        default_version="v1",
        description="OpenApi",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/members/", include("member.urls")),
    path("oauth/", include("member.oauth_urls")),
    path("api/diary/", include("diary.urls")),
    path("api/diary/recommendation-keyword", include("diary.ai_urls")),
    path("api/diary/music/", include("diary.music_urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger-ui",
    ),
]
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
