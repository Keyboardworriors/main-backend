import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import MemberInfo, SocialAccount
from member.serializer import (
    SocialAccountSerializer,
    MemberInfoSerializer,
    ProfileSerializer,
)
from member.views import CreateMemberInfo  # Import necessary view


class CreateMemberInfoViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:member_info_register")
        self.social_account = SocialAccount.objects.create(email="test@example.com", provider="kakao", provider_user_id="123")
        self.refresh_token = RefreshToken.for_user(self.social_account)
        self.access_token = self.refresh_token.access_token

    def test_get_request_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_request_with_valid_data(self):
        data = {"email": "test@example.com", "nickname": "newnickname", "introduce": "new introduce", "favorite_genre": ["SF"]}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["nickname"], "newnickname")
        self.assertTrue(SocialAccount.objects.get(email="test@example.com").is_active)
        self.assertTrue(MemberInfo.objects.filter(social_account_id=self.social_account.social_account_id).exists())

    def test_post_request_with_invalid_data(self):
        data = {"email": "test@example.com", "nickname": "longnickname" * 10, "introduce": "introduce", "favorite_genre": ["SF"]}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data)

    def test_post_request_social_account_not_found(self):
        data = {"email": "nonexistent@example.com", "nickname": "nickname", "introduce": "introduce", "favorite_genre": ["SF"]}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "소셜 계정을 찾을 수 없습니다")


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:login")
        self.social_account = SocialAccount.objects.create(email="test@example.com", provider="kakao", provider_user_id="123", is_active=True)
        self.member_info = MemberInfo.objects.create(nickname="existingnickname", social_account=self.social_account)

    def test_post_request_valid_login(self):
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["nickname"], "existingnickname")

    def test_post_request_unregistered_user(self):
        social_account_inactive = SocialAccount.objects.create(email="inactive@example.com", provider="naver", provider_user_id="456", is_active=False)
        MemberInfo.objects.create(nickname="inactiveuser", social_account=social_account_inactive)
        data = {"email": "inactive@example.com"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "회원 정보 등록이 필요합니다")


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:logout")
        self.social_account = SocialAccount.objects.create(email="test@example.com", provider="kakao", provider_user_id="123", is_active=True)
        self.refresh_token = RefreshToken.for_user(self.social_account)
        self.access_token = str(self.refresh_token.access_token) # Access token string

    def test_post_request_valid_logout(self):
        data = {"refresh_token": str(self.refresh_token)}
        response = self.client.post(self.url, data, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Successfully Logout")
        # Blacklist check requires additional logic

    def test_post_request_invalid_token(self):
        data = {"refresh_token": "invalid_token"}
        response = self.client.post(self.url, data, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "Token is invalid") # Check for a more specific error

    def test_post_request_missing_refresh_token(self):
        response = self.client.post(self.url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "Invalid Token")
class MemberMypageViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:mypage")
        self.social_account = SocialAccount.objects.create(email="test@example.com", provider="kakao", provider_user_id="123", is_active=True)
        self.member_info = MemberInfo.objects.create(nickname="test", social_account=self.social_account)
        self.refresh_token = RefreshToken.for_user(self.social_account)
        self.access_token = str(self.refresh_token.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_get_request_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_request_update_info_success(self):
        data = {"nickname": "newnickname", "introduce": "new introduce"}
        response = self.client.patch(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "newnickname")
        self.assertEqual(response.data["introduce"], "new introduce")

    def test_patch_request_update_info_failure(self):
        data = {"nickname": "longnickname" * 10}
        response = self.client.patch(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data["errors"])

    def test_delete_request_delete_account(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Successfully deleted")
        self.assertFalse(SocialAccount.objects.filter(email="test@example.com").exists())


class MemberProfileViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:profile")
        self.social_account = SocialAccount.objects.create(email="test@example.com", provider="kakao", provider_user_id="123", profile_image="http://example.com/image.jpg", is_active=True)
        self.member_info = MemberInfo.objects.create(nickname="test", introduce="introduce", favorite_genre=["action"], social_account=self.social_account)
        self.refresh_token = RefreshToken.for_user(self.social_account)
        self.access_token = str(self.refresh_token.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_get_request_profile_info(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile_image"], "http://example.com/image.jpg")
        self.assertEqual(response.data["member"]["nickname"], "test")
        self.assertEqual(response.data["member"]["introduce"], "introduce")
        self.assertEqual(response.data["member"]["favorite_genre"], ["action"])
