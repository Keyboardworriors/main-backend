import json
import random
import string
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from member.models import Member, SocialAccount

User = get_user_model()


class KakaoLoginCallbackTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("oauth:kakao_login_callback")
        self.test_email = "test@example.com"
        self.test_nickname = "testuser"

    @patch("requests.post")
    def test_kakao_callback_missing_code(self, mock_post):
        """인가 코드 없이 요청 시 400 응답"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("requests.post")
    @patch("requests.get")
    def test_kakao_callback_success(self, mock_get, mock_post):
        """카카오 로그인 성공 테스트"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access_token": "test_token"
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": "123456",
            "kakao_account": {
                "email": self.test_email,
                "profile": {"profile_image_url": "http://test.com/image.jpg"},
            },
        }

        response = self.client.get(self.url, {"code": "testcode"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.json())
        self.assertIn("refresh_token", response.json())

        # 소셜 계정 생성 여부 확인
        social_account = SocialAccount.objects.filter(
            provider="kakao", provider_user_id="123456"
        ).first()
        self.assertIsNotNone(social_account)
        self.assertEqual(social_account.email, self.test_email)

        # 멤버 생성 여부 확인
        member = Member.objects.filter(email=self.test_email).first()
        self.assertIsNotNone(member)

        # 소셜 계정에 멤버가 제대로 연결되었는지 확인
        self.assertEqual(social_account.member, member)

    def tearDown(self):
        SocialAccount.objects.all().delete()
        Member.objects.all().delete()


class NaverLoginCallbackTest(APITestCase):
    # Given
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("oauth:naver_login_callback")
        self.test_email = "test@naver.com"
        self.test_nickname = "testnaveruser"

    @patch("requests.post")
    def test_naver_callback_missing_code(self, mock_post):
        """인가 코드 없이 요청 시 400 응답"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("requests.post")
    @patch("requests.get")
    def test_naver_callback_success(self, mock_get, mock_post):
        """네이버 로그인 성공 테스트"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access_token": "naver_test_token"
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "response": {
                "id": "654321",
                "email": self.test_email,
                "profile_image": "http://naver.com/profile.jpg",
            }
        }

        response = self.client.get(self.url, {"code": "testcode"})
        # token 여부 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.json())
        self.assertIn("refresh_token", response.json())

        # 소셜 계정 생성 여부 확인
        social_account = SocialAccount.objects.filter(
            provider="naver", provider_user_id="654321"
        ).first()
        self.assertIsNotNone(social_account)
        self.assertEqual(social_account.email, self.test_email)

        # 멤버 생성 여부 확인
        member = Member.objects.filter(email=self.test_email).first()
        self.assertIsNotNone(member)

        # 소셜 계정에 멤버가 제대로 연결되었는지 확인
        self.assertEqual(social_account.member, member)

    # Test DB 정리
    def tearDown(self):
        SocialAccount.objects.all().delete()
        Member.objects.all().delete()
