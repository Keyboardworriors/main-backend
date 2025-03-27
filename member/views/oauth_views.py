import requests
from django.forms.models import model_to_dict
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from psycopg2 import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from member.models import SocialAccount
from member.serializer import (
    SocialAccountInfoSerializer,
    SocialAccountSerializer,
)


class KakaoLoginCallback(APIView):
    @swagger_auto_schema(
        operation_summary="Kakao Login Callback API",
        operation_description="Handles the callback after Kakao login, processes the authorization code, and creates/retrieves the social account.",
        manual_parameters=[
            openapi.Parameter(
                name="code",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Authorization code received from Kakao",
                required=True,
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Successful login or account connection",
                schema=SocialAccountInfoSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {"error": "Code is missing"},
                    "application/json": {
                        "email": ["Please provide an email address."]
                    },
                    "application/json": {
                        "error": "This email address is already in use."
                    },
                },
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Failed to communicate with Kakao API",
                examples={
                    "application/json": {
                        "error": "Failed to get Kakao access token"
                    },
                    "application/json": {"error": "Kakao User Info Error: ..."},
                },
            ),
        },
    )
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response(
                {"error": "Code is missing"}, status=status.HTTP_400_BAD_REQUEST
            )
        access_token = self.get_access_kakao_token(code)
        if not access_token:
            return Response(
                {"error": "Failed to get Kakao access token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        member_info = self.get_member_info_kakao(access_token)
        if "error" in member_info:
            return Response(
                member_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        social_account = self.get_or_create_social_account(member_info)
        if social_account.get("error"):
            return Response(
                {"error": social_account.get("error")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SocialAccountInfoSerializer(data=social_account)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_access_kakao_token(self, code):
        print(f"Received code: {code}")
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
            print(response.json())  # 응답 내용 확인
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.RequestException as e:
            print(f"Kakao token request error: {str(e)}")  # 오류 로그 추가
            return None

    def get_member_info_kakao(self, access_token):
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(url, headers=headers)
            print("Get MemberInfo data:", response)
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
                return {"error": "An account with this email already exists."}

            social_account = SocialAccount.objects.create(
                provider="kakao",
                provider_user_id=provider_user_id,
                email=email,
                profile_image=profile_image,
                is_active=False,
            )

        social_account_dict = model_to_dict(social_account)
        return social_account_dict


class NaverLoginCallback(APIView):
    @swagger_auto_schema(
        operation_summary="Naver Login Callback API",
        operation_description="Handles the callback after Naver login, processes the authorization code, and creates/retrieves the social account.",
        manual_parameters=[
            openapi.Parameter(
                name="code",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Authorization code received from Naver",
                required=True,
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Successful login or account connection",
                schema=SocialAccountInfoSerializer,
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {"error": "missing code"},
                    "application/json": {"provider": ["Invalid provider"]},
                    "application/json": {"email": ["Invalid email"]},
                },
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(
                description="Failed to communicate with Naver API",
                examples={
                    "application/json": {
                        "error": "Failed to get Naver access token"
                    },
                    "application/json": {"error": "Naver User Info Error: ..."},
                },
            ),
        },
    )
    def get(self, request):
        code = request.GET.get("code")
        if not code:
            return Response(
                {"error": "missing code"}, status=status.HTTP_400_BAD_REQUEST
            )
        access_token = self.get_access_naver_token(code)
        if not access_token:
            return Response(
                {"error": "Failed to get Naver access token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        member_info = self.get_member_info_naver(access_token)
        if "error" in member_info:
            return Response(
                member_info, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        social_account = self.get_or_create_social_account(member_info)
        if social_account.get("error"):
            return Response(
                {"error": social_account.get("error")},
                status=status.HTTP_400_BAD_REQUEST,
            )
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

        social_account = SocialAccount.objects.filter(
            provider="naver", provider_user_id=provider_user_id
        ).first()

        if not social_account:
            if SocialAccount.objects.filter(email=email).exists():
                return {"error": "An account with this email already exists."}

            social_account = SocialAccount.objects.create(
                provider="naver",
                provider_user_id=provider_user_id,
                email=email,
                profile_image=profile_image,
                is_active=False,
            )

        social_account_dict = model_to_dict(social_account)
        return social_account_dict
