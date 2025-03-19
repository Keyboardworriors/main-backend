from django.urls.conf import path

from member.oauth_views import KakaoLoginCallback, NaverLoginCallback

app_name = "oauth"

urlpatterns = [
    path(
        "kakao/callback/",
        KakaoLoginCallback.as_view(),
        name="kakao_login_callback",
    ),
    path(
        "naver/callback/",
        NaverLoginCallback.as_view(),
        name="naver_login_callback",
    ),
]
