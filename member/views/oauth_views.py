import logging

import requests
from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from member.models import SocialAccount
from member.serializer import SocialAccountInfoSerializer

logger = logging.getLogger(__name__)  # logger 객체 생성


class KakaoLoginCallback(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            logger.warning("Kakao login attempt without code")
            return Response(
                {"error": "Code is missing"}, status=status.HTTP_400_BAD_REQUEST
            )
        access_token = self.get_access_kakao_token(code)
        if not access_token:
            logger.error("Failed to get Kakao access token")
            return Response(
                {"error": "Failed to get Kakao access token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        member_info = self.get_member_info_kakao(access_token)
        if "error" in member_info:
            logger.error(f"Kakao user info error: {member_info['error']}")
            return Response(
                member_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        social_account = self.get_or_create_social_account(member_info)
        if social_account.get("error"):
            logger.warning(
                f"Social account creation error: {social_account['error']}"
            )
            return Response(
                {"error": social_account.get("error")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SocialAccountInfoSerializer(data=social_account)
        if serializer.is_valid():
            logger.info(
                f"Successful Kakao login for user: {social_account['email']}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.warning(f"Serializer validation error: {serializer.errors}")
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
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.RequestException as e:
            logger.error(f"Kakao token request error: {str(e)}")
            return None

    def get_member_info_kakao(self, access_token):
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Kakao user info request error: {str(e)}")
            return {"error": f"Kakao User Info Error: {str(e)}"}

    def get_or_create_social_account(self, member_info):
        kakao_account = member_info.get("kakao_account", {})
        email = kakao_account.get("email")
        profile = kakao_account.get("profile", {})
        profile_image = profile.get("profile_image_url", "")
        provider_user_id = str(member_info["id"])

        try:
            social_account = SocialAccount.objects.get(
                provider="kakao", provider_user_id=provider_user_id
            )
            logger.info(f"Existing Kakao account found for user: {email}")
        except SocialAccount.DoesNotExist:
            if SocialAccount.objects.filter(email=email).exists():
                logger.warning(f"Account with email {email} already exists")
                return {"error": "An account with this email already exists."}

            social_account = SocialAccount.objects.create(
                provider="kakao",
                provider_user_id=provider_user_id,
                email=email,
                profile_image=profile_image,
                is_active=False,
            )
            logger.info(f"New Kakao account created for user: {email}")

        return model_to_dict(social_account)


class NaverLoginCallback(APIView):
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            logger.warning("Naver login attempt without code")
            return Response(
                {"error": "missing code"}, status=status.HTTP_400_BAD_REQUEST
            )
        access_token = self.get_access_naver_token(code)
        if not access_token:
            logger.error("Failed to get Naver access token")
            return Response(
                {"error": "Failed to get Naver access token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        member_info = self.get_member_info_naver(access_token)
        if "error" in member_info:
            logger.error(f"Naver user info error: {member_info['error']}")
            return Response(
                member_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        social_account = self.get_or_create_social_account(member_info)
        if social_account.get("error"):
            logger.warning(
                f"Social account creation error: {social_account['error']}"
            )
            return Response(
                {"error": social_account.get("error")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SocialAccountInfoSerializer(data=social_account)
        if serializer.is_valid():
            logger.info(
                f"Successful Naver login for user: {social_account['email']}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.warning(f"Serializer validation error: {serializer.errors}")
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
            logger.error(f"Naver token request error: {str(e)}")
            return None

    def get_member_info_naver(self, access_token):
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get("response", {})
        except requests.RequestException as e:
            logger.error(f"Naver user info request error: {str(e)}")
            return {"error": f"Naver User Info Error: {str(e)}"}

    def get_or_create_social_account(self, member_info):
        email = member_info.get("email")
        profile_image = member_info.get("profile_image")
        provider_user_id = str(member_info.get("id"))

        try:
            social_account = SocialAccount.objects.get(
                provider="naver", provider_user_id=provider_user_id
            )
            logger.info(f"Existing Naver account found for user: {email}")
        except SocialAccount.DoesNotExist:
            if SocialAccount.objects.filter(email=email).exists():
                logger.warning(f"Account with email {email} already exists")
                return {"error": "An account with this email already exists."}

            social_account = SocialAccount.objects.create(
                provider="naver",
                provider_user_id=provider_user_id,
                email=email,
                profile_image=profile_image,
                is_active=False,
            )
            logger.info(f"New Naver account created for user: {email}")

        return model_to_dict(social_account)
