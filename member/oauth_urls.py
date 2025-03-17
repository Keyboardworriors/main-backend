from django.urls.conf import path

from member.oauth_views import KakaoLoginCallback, NaverLoginCallback

app_name = "oauth"

urlpatterns = [
    path(
        "api/kakao/callback", KakaoLoginCallback.as_view(), name="kakao_oauth"
    ),
    path(
        "api/naver/callback", NaverLoginCallback.as_view(), name="naver_oauth"
    ),
]
