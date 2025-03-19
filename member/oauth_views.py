import requests
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.views import APIView, Response

from config import settings
from config.settings import (
    KAKAO_CLIENT_ID,
    KAKAO_REDIRECT_URL,
    KAKAO_SECRET,
)
from member.models import Member, SocialAccount


class KakaoLoginCallback(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Code is missing"}, status=400)
        access_token = self.get_access_kakao_token(code)
        member_info = self.get_member_info_kakao(access_token)
        social_account = self.get_or_create_social_account(member_info)
        social_account_data = {
            "provider": social_account.provider,
            "provider_user_id": social_account.provider_user_id,
            "email": social_account.email,
            "profile_image": social_account.profile_image,
            "member_id": (
                str(social_account.member.id) if social_account.member else None
            ),
            # UUID -> 문자열
        }

        # 세션에 저장
        request.session["social_account"] = social_account_data
        if not Member.objects.filter(email=social_account.email).exists():
            return HttpResponseRedirect(reverse("member:register"))
        return HttpResponseRedirect(reverse("member:login"))

    # 카카오에서 access_token 받아오기
    def get_access_kakao_token(self, code):
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_CLIENT_ID,
            "client_secret": KAKAO_SECRET,
            "redirect_uri": KAKAO_REDIRECT_URL,
            "code": code,
        }
        response = requests.post(url, data=data)
        response_data = response.json()
        if response.status_code == 200:
            return response_data["access_token"]
        else:
            return None

    # 카카오에서 멤버 정보 받아오기
    def get_member_info_kakao(self, access_token):
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def get_or_create_social_account(self, member_info):
        kakao_account = member_info.get("kakao_account", {})
        email = kakao_account.get("email")
        profile_image = kakao_account.get("profile", {}).get(
            "profile_image_url", ""
        )
        provider_user_id = str(member_info["id"])

        social_account, _ = SocialAccount.objects.get_or_create(
            provider="kakao",
            provider_user_id=provider_user_id,
            defaults={"email": email, "profile_image": profile_image},
        )

        return social_account


class NaverLoginCallback(APIView):

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "missing code"}, status=400)
        access_token = self.get_access_naver_token(code)
        member_info = self.get_member_info_naver(access_token)
        social_account = self.get_or_create_social_account(member_info)

        request.session["social_account"] = model_to_dict(social_account)
        if not Member.objects.filter(email=social_account.email).exists():
            return HttpResponseRedirect(reverse("member:register"))
        return HttpResponseRedirect(reverse("member:login"))

    def get_access_naver_token(self, code):
        """네이버 OAuth 토큰 요청 (쿼리 파라미터 사용)"""
        url = "https://nid.naver.com/oauth2.0/token"
        params = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_SECRET,
            "redirect_uri": settings.NAVER_REDIRECT_URL,
            "code": code,
        }
        response = requests.post(url, params=params)
        response_data = response.json()
        return response_data.get("access_token")

    def get_member_info_naver(self, access_token):
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        return response.json().get("response", {})

    # 소셜 어카운트 조회 혹은 생성
    def get_or_create_social_account(self, member_info):
        email = member_info.get("email")
        profile_image = member_info.get("profile_image_url", "")
        provider_user_id = str(member_info.get("id"))

        social_account, _ = SocialAccount.objects.get_or_create(
            provider="naver",
            provider_user_id=provider_user_id,
            defaults={"email": email, "profile_image": profile_image},
        )

        return social_account
