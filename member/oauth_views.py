import requests
from django.forms.models import model_to_dict
from psycopg2 import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from member.models import SocialAccount
from member.serializer import SocialAccountInfoSerializer, \
    SocialAccountSerializer


class KakaoLoginCallback(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Code is missing"}, status=status.HTTP_400_BAD_REQUEST)
        access_token = self.get_access_kakao_token(code)
        if not access_token:
            return Response(
                {"error": "Failed to get Kakao access token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        member_info = self.get_member_info_kakao(access_token)
        if "error" in member_info:
            return Response(member_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        social_account = self.get_or_create_social_account(member_info)
        if social_account.get("error"):
            return Response({"error":social_account.get("error")}, status=400)
        serializer = SocialAccountInfoSerializer(data=social_account)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_access_kakao_token(self, code):
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "client_secret": settings.KAKAO_SECRET,
            "redirect_uri": settings.KAKAO_REDIRECT_URL,
            "code": code,
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.RequestException as e:
            return None

    def get_member_info_kakao(self, access_token):
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Kakao User Info Error: {str(e)}"}

    def get_or_create_social_account(self, member_info):
        kakao_account = member_info["kakao_account"] or {}
        email = kakao_account.get("email")
        profile = kakao_account.get("profile")
        profile_image = profile.get("profile_image_url") or ""
        provider_user_id = str(member_info["id"])
        social_account = SocialAccount.objects.filter(
            provider="kakao", provider_user_id=provider_user_id
        ).first()

        if not social_account:
            if SocialAccount.objects.filter(email=email).exists():
                return {"error": "이미 해당 이메일이 존재합니다."}

            social_account = SocialAccount.objects.create(
                provider="kakao",
                provider_user_id=provider_user_id,
                email=email,
                profile_image=profile_image,
                is_active=False
            )

        social_account_dict = model_to_dict(social_account)
        return social_account_dict


class NaverLoginCallback(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "missing code"}, status=status.HTTP_400_BAD_REQUEST)
        access_token = self.get_access_naver_token(code)
        if not access_token:
            return Response(
                {"error": "Failed to get Naver access token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        member_info = self.get_member_info_naver(access_token)
        if "error" in member_info:
            return Response(member_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        social_account = self.get_or_create_social_account(member_info)
        serializer = SocialAccountInfoSerializer(data=social_account)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_access_naver_token(self, code):
        url = "https://nid.naver.com/oauth2.0/token"
        params = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_SECRET,
            "redirect_uri": settings.NAVER_REDIRECT_URL,
            "code": code,
        }
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.RequestException as e:
            return None

    def get_member_info_naver(self, access_token):
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get("response", {})
        except requests.RequestException as e:
            return {"error": f"Naver User Info Error: {str(e)}"}

    def get_or_create_social_account(self, member_info):
        email = member_info.get("email")
        profile_image = member_info.get("profile_image")
        provider_user_id = str(member_info.get("id"))

        social_account, _ = SocialAccount.objects.get_or_create(
            provider="naver",
            provider_user_id=provider_user_id,
            defaults={
                "email": email,
                "profile_image": profile_image,
            },
        )

        return  model_to_dict(social_account)
