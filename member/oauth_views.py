import requests
from django.contrib.auth import login
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken

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
        member = self.get_or_create_member(social_account, member_info)

        login(request, member)
        refresh = RefreshToken.for_user(member)
        return Response(
            {
                "message": "Successfully logined",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": member,
            }
        )

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

    # 소셜 어카운트 조회 혹은 생성
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

    # 멤버 조회 또는 생성
    def get_or_create_member(self, social_account, member_info):
        if social_account.member:
            return social_account.member
        nickname = (
            member_info.get("kakao_account", {})
            .get("profile", {})
            .get("nickname", "")
        )

        member = Member.objects.create_user(
            email=social_account.email, nickname=nickname
        )
        social_account.member = member
        social_account.save()
        return member


class NaverLoginCallback(APIView):

    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "missing code"}, status=400)
        access_token = self.get_access_naver_token(code)
        member_info = self.get_member_info_naver(access_token)
        social_account = self.get_or_create_social_account(member_info)
        member = self.get_or_create_member(social_account, member_info)
        login(request, member)
        refresh = RefreshToken.for_user(member)
        return Response(
            {
                "message": "Successfully logined",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": member,
            }
        )

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

    # 멤버 조회 또는 생성
    def get_or_create_member(self, social_account, member_info):
        if social_account.member:
            return social_account.member
        nickname = member_info["response"]["nickname"]

        member = Member.objects.create_user(
            email=social_account.email, nickname=nickname
        )
        social_account.member = member
        social_account.save()
        return member
