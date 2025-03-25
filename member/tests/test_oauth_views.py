import json

import responses
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from member.models import SocialAccount


@override_settings(
    KAKAO_CLIENT_ID="test_kakao_client_id",
    KAKAO_SECRET="test_kakao_secret",
    KAKAO_REDIRECT_URL="http://localhost:8000/member/kakao/callback/",
    NAVER_CLIENT_ID="test_naver_client_id",
    NAVER_SECRET="test_naver_secret",
    NAVER_REDIRECT_URL="http://localhost:8000/member/naver/callback/",
)
class KakaoLoginCallbackTestWithoutMock(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.callback_url = reverse("oauth:kakao_login_callback")

    @responses.activate
    def test_kakao_login_success_new_user(self):
        code = "test_code"
        access_token = "test_access_token"
        kakao_user_info = {
            "id": 12345,
            "kakao_account": {
                "email": "new_user@example.com",
                "profile": {
                    "profile_image_url": "http://example.com/image.jpg"
                },
            },
        }

        responses.post(
            "https://kauth.kakao.com/oauth/token",
            json={"access_token": access_token},
        )
        responses.get(
            "https://kapi.kakao.com/v2/user/me",
            json=kakao_user_info,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response = self.client.get(self.callback_url, {"code": code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["provider"], "kakao")
        self.assertEqual(response.data["email"], "new_user@example.com")
        self.assertEqual(
            response.data["profile_image"], "http://example.com/image.jpg"
        )
        self.assertTrue(
            SocialAccount.objects.filter(
                provider="kakao", provider_user_id="12345"
            ).exists()
        )

    @responses.activate
    def test_kakao_login_success_existing_user(self):
        code = "test_code"
        access_token = "test_access_token"
        kakao_user_info = {
            "id": 12345,
            "kakao_account": {
                "email": "existing_user@example.com",
                "profile": {
                    "profile_image_url": "http://example.com/image.jpg"
                },
            },
        }
        SocialAccount.objects.create(
            provider="kakao",
            provider_user_id="12345",
            email="existing_user@example.com",
            profile_image="http://example.com/image.jpg",
        )

        responses.post(
            "https://kauth.kakao.com/oauth/token",
            json={"access_token": access_token},
        )
        responses.get(
            "https://kapi.kakao.com/v2/user/me",
            json=kakao_user_info,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response = self.client.get(self.callback_url, {"code": code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["provider"], "kakao")
        self.assertEqual(response.data["email"], "existing_user@example.com")
        self.assertEqual(
            response.data["profile_image"], "http://example.com/image.jpg"
        )
        self.assertTrue(
            SocialAccount.objects.filter(
                provider="kakao", provider_user_id="12345"
            ).exists()
        )
        self.assertEqual(
            SocialAccount.objects.get(
                provider="kakao", provider_user_id="12345"
            ).email,
            "existing_user@example.com",
        )

    @responses.activate
    def test_kakao_login_failure_missing_code(self):
        response = self.client.get(self.callback_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Code is missing")

    @responses.activate
    def test_kakao_login_failure_get_access_token(self):
        code = "test_code"
        responses.post(
            "https://kauth.kakao.com/oauth/token",
            status=400,
            json={
                "error": "invalid_grant",
                "error_description": "Authorization code expired",
            },
        )
        response = self.client.get(self.callback_url, {"code": code})
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertEqual(
            response.data["error"], "Failed to get Kakao access token"
        )

    @responses.activate
    def test_kakao_login_failure_get_member_info(self):
        code = "test_code"
        access_token = "test_access_token"
        responses.post(
            "https://kauth.kakao.com/oauth/token",
            json={"access_token": access_token},
        )
        responses.get(
            "https://kapi.kakao.com/v2/user/me",
            status=401,
            json={"msg": "unauthorized", "code": -401},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response = self.client.get(self.callback_url, {"code": code})
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertIn("Kakao User Info Error", response.data["error"])

    @responses.activate
    def test_kakao_login_existing_email(self):
        code = "test_code"
        access_token = "test_access_token"
        kakao_user_info = {
            "id": 12345,
            "kakao_account": {
                "email": "existing_email@example.com",
                "profile": {
                    "profile_image_url": "http://example.com/image.jpg"
                },
            },
        }
        SocialAccount.objects.create(
            provider="naver", email="existing_email@example.com"
        )

        responses.post(
            "https://kauth.kakao.com/oauth/token",
            json={"access_token": access_token},
        )
        responses.get(
            "https://kapi.kakao.com/v2/user/me",
            json=kakao_user_info,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response = self.client.get(self.callback_url, {"code": code})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"], "An account with this email already exists."
        )


@override_settings(
    KAKAO_CLIENT_ID="test_kakao_client_id",
    KAKAO_SECRET="test_kakao_secret",
    KAKAO_REDIRECT_URL="http://localhost:8000/member/kakao/callback/",
    NAVER_CLIENT_ID="test_naver_client_id",
    NAVER_SECRET="test_naver_secret",
    NAVER_REDIRECT_URL="http://localhost:8000/member/naver/callback/",
)
class NaverLoginCallbackTestWithoutMock(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.callback_url = reverse("oauth:naver_login_callback")

    @responses.activate
    def test_naver_login_success_new_user(self):
        code = "test_code"
        access_token = "test_access_token"
        naver_user_info = {
            "resultcode": "00",
            "message": "success",
            "response": {
                "id": "67890",
                "email": "new_user@naver.com",
                "profile_image": "http://example.com/naver_image.jpg",
            },
        }

        responses.post(
            "https://nid.naver.com/oauth2.0/token",
            json={"access_token": access_token},
        )
        responses.get(
            "https://openapi.naver.com/v1/nid/me",
            json=naver_user_info,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response = self.client.get(self.callback_url, {"code": code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["provider"], "naver")
        self.assertEqual(response.data["provider_user_id"], "67890")
        self.assertEqual(response.data["email"], "new_user@naver.com")
        self.assertEqual(
            response.data["profile_image"], "http://example.com/naver_image.jpg"
        )
        self.assertTrue(
            SocialAccount.objects.filter(
                provider="naver", provider_user_id="67890"
            ).exists()
        )

    @responses.activate
    def test_naver_login_success_existing_user(self):
        code = "test_code"
        access_token = "test_access_token"
        naver_user_info = {
            "resultcode": "00",
            "message": "success",
            "response": {
                "id": "67890",
                "email": "existing_user@naver.com",
                "profile_image": "http://example.com/naver_image.jpg",
            },
        }
        SocialAccount.objects.create(
            provider="naver",
            provider_user_id="67890",
            email="existing_user@naver.com",
            profile_image="http://example.com/naver_image.jpg",
        )

        responses.post(
            "https://nid.naver.com/oauth2.0/token",
            json={"access_token": access_token},
        )
        responses.get(
            "https://openapi.naver.com/v1/nid/me",
            json=naver_user_info,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response = self.client.get(self.callback_url, {"code": code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["provider"], "naver")
        self.assertEqual(response.data["email"], "existing_user@naver.com")
        self.assertEqual(
            response.data["profile_image"], "http://example.com/naver_image.jpg"
        )
        self.assertTrue(
            SocialAccount.objects.filter(
                provider="naver", provider_user_id="67890"
            ).exists()
        )
        self.assertEqual(
            SocialAccount.objects.get(
                provider="naver", provider_user_id="67890"
            ).email,
            "existing_user@naver.com",
        )

    @responses.activate
    def test_naver_login_failure_missing_code(self):
        response = self.client.get(self.callback_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "missing code")

    @responses.activate
    def test_naver_login_failure_get_access_token(self):
        code = "test_code"
        responses.post(
            "https://nid.naver.com/oauth2.0/token",
            status=400,
            json={
                "error": "invalid_request",
                "error_description": "The authorization code is invalid.",
            },
        )
        response = self.client.get(self.callback_url, {"code": code})
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertEqual(
            response.data["error"], "Failed to get Naver access token"
        )

    @responses.activate
    def test_naver_login_failure_get_member_info(self):
        code = "test_code"
        access_token = "test_access_token"
        responses.post(
            "https://nid.naver.com/oauth2.0/token",
            json={"access_token": access_token},
        )
        responses.get(
            "https://openapi.naver.com/v1/nid/me",
            status=401,
            json={"resultcode": "01", "message": "error"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response = self.client.get(self.callback_url, {"code": code})
        self.assertEqual(
            response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.assertIn("Naver User Info Error", response.data["error"])
