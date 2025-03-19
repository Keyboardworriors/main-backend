# tests/test_oauth.py
from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from member.models import Member, SocialAccount


# 기본 테스트 설정
class OAuthBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.register_url = reverse("member:register")
        cls.login_url = reverse("member:login")


# 카카오 테스트 케이스
class KakaoLoginCallbackTest(OAuthBaseTest):
    def setUp(self):
        self.url = reverse("oauth:kakao_login_callback")
        self.mock_user_data = {
            "id": 123456789,
            "kakao_account": {
                "email": "test@kakao.com",
                "profile": {
                    "profile_image_url": "http://kakao.com/profile.jpg"
                },
            },
        }

    # Case 1: 코드 누락
    def test_missing_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Code is missing"})

    # Case 2: 유효한 코드 (신규 사용자)
    @patch("member.views.requests.get")
    @patch("member.views.requests.post")
    def test_valid_code_new_user(self, mock_post, mock_get):
        # Access Token 요청 모킹
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"access_token": "mock_token"}),
        )

        # 사용자 정보 요청 모킹
        mock_get.return_value = Mock(
            status_code=200, json=Mock(return_value=self.mock_user_data)
        )

        response = self.client.get(self.url, {"code": "valid_code"})
        self.assertRedirects(response, self.register_url)

        # 소셜 계정 생성 확인
        social_account = SocialAccount.objects.get(provider="kakao")
        self.assertEqual(social_account.email, "test@kakao.com")
        self.assertEqual(social_account.provider_user_id, "123456789")

    # Case 3: 기존 사용자
    @patch("member.views.requests.get")
    @patch("member.views.requests.post")
    def test_valid_code_existing_user(self, mock_post, mock_get):
        # 기존 사용자 생성
        SocialAccount.objects.create(
            provider="kakao",
            provider_user_id="123456789",
            email="test@kakao.com",
        )
        Member.objects.create(email="test@kakao.com")

        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"access_token": "mock_token"}),
        )
        mock_get.return_value = Mock(
            status_code=200, json=Mock(return_value=self.mock_user_data)
        )

        response = self.client.get(self.url, {"code": "valid_code"})
        self.assertRedirects(response, self.login_url)


# 네이버 테스트 케이스
class NaverLoginCallbackTest(OAuthBaseTest):
    def setUp(self):
        self.url = reverse("oauth:naver_login_callback")
        self.mock_user_data = {
            "response": {
                "id": "987654321",
                "email": "test@naver.com",
                "profile_image": "http://naver.com/profile.jpg",
            }
        }

    # Case 1: 코드 누락
    def test_missing_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "missing code"})

    # Case 2: 신규 사용자
    @patch("member.views.requests.get")
    @patch("member.views.requests.post")
    def test_valid_code_new_user(self, mock_post, mock_get):
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"access_token": "mock_token"}),
        )
        mock_get.return_value = Mock(
            status_code=200, json=Mock(return_value=self.mock_user_data)
        )

        response = self.client.get(self.url, {"code": "valid_code"})
        self.assertRedirects(response, self.register_url)

        social_account = SocialAccount.objects.get(provider="naver")
        self.assertEqual(social_account.email, "test@naver.com")
        self.assertEqual(social_account.provider_user_id, "987654321")

    # Case 3: 기존 사용자
    @patch("member.views.requests.get")
    @patch("member.views.requests.post")
    def test_valid_code_existing_user(self, mock_post, mock_get):
        SocialAccount.objects.create(
            provider="naver",
            provider_user_id="987654321",
            email="test@naver.com",
        )
        Member.objects.create(email="test@naver.com")

        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"access_token": "mock_token"}),
        )
        mock_get.return_value = Mock(
            status_code=200, json=Mock(return_value=self.mock_user_data)
        )

        response = self.client.get(self.url, {"code": "valid_code"})
        self.assertRedirects(response, self.login_url)
