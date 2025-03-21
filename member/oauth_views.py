import requests
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from member.models import SocialAccount


class KakaoLoginCallback(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Code is missing"}, status=400)
        access_token = self.get_access_kakao_token(code)
        if not access_token:
            return Response(
                {"error": "Failed to get Kakao access token"}, status=500
            )
        member_info = self.get_member_info_kakao(access_token)
        if "error" in member_info:
            return Response(member_info, status=500)
        social_account = self.get_or_create_social_account(member_info)
        social_account_data = {
            "provider": social_account.provider,
            "email": social_account.email,
            "profile_image": social_account.profile_image,
            "is_active": social_account.is_active,
        }
        return Response(social_account_data, status=200)

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
        kakao_account = member_info.get("kakao_account", {})
        email = kakao_account.get("email")
        profile_image = kakao_account.get("profile", {}).get(
            "profile_image_url", ""
        )
        provider_user_id = str(member_info["id"])

        social_account, _ = SocialAccount.objects.get_or_create(
            provider="kakao",
            provider_user_id=provider_user_id,
            defaults={
                "email": email,
                "profile_image": profile_image,
            },
        )
        return social_account


class NaverLoginCallback(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response({"error": "missing code"}, status=400)
        access_token = self.get_access_naver_token(code)
        if not access_token:
            return Response(
                {"error": "Failed to get Naver access token"}, status=500
            )
        member_info = self.get_member_info_naver(access_token)
        if "error" in member_info:
            return Response(member_info, status=500)
        social_account = self.get_or_create_social_account(member_info)
        social_account_data = {
            "provider": social_account.provider,
            "email": social_account.email,
            "profile_image": social_account.profile_image,
            "is_active": social_account.is_active,
        }
        return Response(social_account_data, status=200)

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
        profile_image = member_info.get("profile_image_url", "")
        provider_user_id = str(member_info.get("id"))

        social_account, _ = SocialAccount.objects.get_or_create(
            provider="naver",
            provider_user_id=provider_user_id,
            defaults={
                "email": email,
                "profile_image": profile_image,
            },
        )
        return social_account
