from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from member.models import SocialAccount


class OAuthViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("member.views.requests.post")
    @patch("member.views.requests.get")
    def test_kakao_login_callback(self, mock_get, mock_post):
        # Mock the token response
        mock_post.return_value = Mock(
            status_code=200, json=lambda: {"access_token": "fake_access_token"}
        )

        # Mock the user info response
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "id": 123456789,
                "kakao_account": {
                    "email": "test@kakao.com",
                    "profile": {
                        "profile_image_url": "http://example.com/profile.jpg"
                    },
                },
            },
        )

        response = self.client.get(
            reverse("oauth:kakao_login_callback"), {"code": "fake_code"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@kakao.com")
        self.assertEqual(response.data["provider"], "kakao")

    @patch("member.views.requests.post")
    @patch("member.views.requests.get")
    def test_naver_login_callback(self, mock_get, mock_post):
        # Mock the token response
        mock_post.return_value = Mock(
            status_code=200, json=lambda: {"access_token": "fake_access_token"}
        )

        # Mock the user info response
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "response": {
                    "id": "12345678",
                    "email": "test@naver.com",
                    "profile_image": "http://example.com/naver_profile.jpg",
                }
            },
        )

        response = self.client.get(
            reverse("oauth:naver_login_callback"), {"code": "fake_code"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@naver.com")
        self.assertEqual(response.data["provider"], "naver")

    def test_kakao_login_callback_missing_code(self):
        response = self.client.get(reverse("oauth:kakao_login_callback"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Code is missing")

    def test_naver_login_callback_missing_code(self):
        response = self.client.get(reverse("oauth:naver_login_callback"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "missing code")
