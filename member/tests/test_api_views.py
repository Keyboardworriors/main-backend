import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import MemberInfo, SocialAccount
from member.serializer import (
    MemberInfoSerializer,
    ProfileSerializer,
    SocialAccountSerializer,
)
from member.views.api_views import CreateMemberInfo  # Import necessary view


class CreateMemberInfoViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:member_info_register")
        self.social_account = SocialAccount.objects.create(
            email="test@example.com", provider="kakao", provider_user_id="123"
        )
        self.refresh_token = RefreshToken.for_user(self.social_account)
        self.access_token = self.refresh_token.access_token

    def test_get_request_returns_200(self):
        print("\nCreateMemberInfoView GET 요청 시 200 응답 확인")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_request_with_valid_data(self):
        print("\nCreateMemberInfoView POST 요청 시 유효한 데이터 처리 확인")
        request_data = {
            "email": "test@example.com",
            "nickname": "newnickname",
            "introduce": "new introduce",
            "favorite_genre": ["SF"],
        }
        response = self.client.post(
            self.url, json.dumps(request_data), content_type="application/json"
        )

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print(f"Response data (400 error): {response.data}")

        social_account_from_db = SocialAccount.objects.get(
            email="test@example.com"
        )
        serializer_data = {
            "nickname": request_data["nickname"],
            "introduce": request_data["introduce"],
            "favorite_genre": request_data["favorite_genre"],
            "social_account": social_account_from_db.social_account_id,
        }
        serializer = MemberInfoSerializer(data=serializer_data)
        if not serializer.is_valid():
            print(f"Serializer errors in test: {serializer.errors}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["nickname"], "newnickname")
        self.assertTrue(social_account_from_db.is_active)
        self.assertTrue(
            MemberInfo.objects.filter(
                social_account_id=social_account_from_db.social_account_id
            ).exists()
        )

    def test_post_request_with_invalid_data(self):
        print(
            "\nCreateMemberInfoView POST 요청 시 유효하지 않은 데이터 처리 확인"
        )
        data = {
            "email": "test@example.com",
            "nickname": "longnickname" * 10,
            "introduce": "introduce",
            "favorite_genre": ["SF"],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data)

    def test_post_request_social_account_not_found(self):
        print(
            "\nCreateMemberInfoView POST 요청 시 소셜 계정 찾을 수 없는 경우 확인"
        )
        data = {
            "email": "nonexistent@example.com",
            "nickname": "nickname",
            "introduce": "introduce",
            "favorite_genre": ["SF"],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Social account not found")

    def test_post_request_missing_required_fields(self):
        print("\nCreateMemberInfoView POST 요청 시 필수 필드 누락 확인")
        # nickname 누락
        data_missing_nickname = {
            "email": "test@example.com",
            "introduce": "introduce",
            "favorite_genre": ["SF"],
        }
        response_missing_nickname = self.client.post(
            self.url, data_missing_nickname
        )
        self.assertEqual(
            response_missing_nickname.status_code, status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response_missing_nickname.data["error"],
            "Email and nickname are required.",
        )

        # email 누락
        data_missing_email = {
            "nickname": "nickname",
            "introduce": "introduce",
            "favorite_genre": ["SF"],
        }
        response_missing_email = self.client.post(self.url, data_missing_email)
        self.assertEqual(
            response_missing_email.status_code, status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            response_missing_email.data["error"],
            "Email and nickname are required.",
        )


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:login")
        self.social_account = SocialAccount.objects.create(
            email="test@example.com",
            provider="kakao",
            provider_user_id="123",
            is_active=True,
        )
        self.member_info = MemberInfo.objects.create(
            nickname="existingnickname", social_account=self.social_account
        )

    def test_post_request_valid_login(self):
        print("\nLoginView POST 요청 시 유효한 로그인 확인")
        data = {"email": "test@example.com"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["nickname"], "existingnickname")

    def test_post_request_unregistered_user(self):
        print("\nLoginView POST 요청 시 미등록 사용자 처리 확인")
        social_account_inactive = SocialAccount.objects.create(
            email="inactive@example.com",
            provider="naver",
            provider_user_id="456",
            is_active=False,
        )
        MemberInfo.objects.create(
            nickname="inactiveuser", social_account=social_account_inactive
        )
        data = {"email": "inactive@example.com"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"],
            "Member information registration is required",
        )


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:logout")
        self.social_account = SocialAccount.objects.create(
            email="test@example.com",
            provider="kakao",
            provider_user_id="123",
            is_active=True,
        )
        self.refresh_token = RefreshToken.for_user(self.social_account)
        self.access_token = str(
            self.refresh_token.access_token
        )  # Access token string

    def test_post_request_valid_logout(self):
        print("\nLogoutView POST 요청 시 유효한 로그아웃 확인")
        data = {"refresh_token": str(self.refresh_token)}
        response = self.client.post(
            self.url, data, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Successfully logged out")
        # Blacklist check requires additional logic

    def test_post_request_invalid_token(self):
        print("\nLogoutView POST 요청 시 유효하지 않은 토큰 처리 확인")
        data = {"refresh_token": "invalid_token"}
        response = self.client.post(
            self.url, data, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_post_request_missing_refresh_token(self):
        print("\nLogoutView POST 요청 시 refresh 토큰 누락 처리 확인")
        response = self.client.post(
            self.url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "Invalid token")


class MemberMypageViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:mypage")
        self.social_account = SocialAccount.objects.create(
            email="test@example.com",
            provider="kakao",
            provider_user_id="123",
            is_active=True,
        )
        self.member_info = MemberInfo.objects.create(
            nickname="test", social_account=self.social_account
        )
        self.refresh_token = RefreshToken.for_user(self.social_account)
        self.access_token = str(self.refresh_token.access_token)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    def test_get_request_authenticated_user(self):
        print("\nMemberMypageView GET 요청 시 인증된 사용자 확인")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_request_update_info_success(self):
        print("\nMemberMypageView PATCH 요청 시 정보 업데이트 성공 확인")
        data = {"nickname": "newnickname", "introduce": "new introduce"}
        response = self.client.patch(
            self.url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "newnickname")
        self.assertEqual(response.data["introduce"], "new introduce")

    def test_patch_request_update_info_failure(self):
        print("\nMemberMypageView PATCH 요청 시 정보 업데이트 실패 확인")
        data = {"nickname": "longnickname" * 10}
        response = self.client.patch(
            self.url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nickname", response.data["errors"])

    def test_delete_request_delete_account(self):
        print("\nMemberMypageView DELETE 요청 시 계정 삭제 확인")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Successfully deleted")
        self.assertFalse(
            SocialAccount.objects.filter(email="test@example.com").exists()
        )


class MemberProfileViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("member:profile")
        self.social_account = SocialAccount.objects.create(
            email="test@example.com",
            provider="kakao",
            provider_user_id="123",
            profile_image="http://example.com/image.jpg",
            is_active=True,
        )
        self.member_info = MemberInfo.objects.create(
            nickname="test",
            introduce="introduce",
            favorite_genre=["action"],
            social_account=self.social_account,
        )
        self.refresh_token = RefreshToken.for_user(self.social_account)
        self.access_token = str(self.refresh_token.access_token)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    def test_get_request_profile_info(self):
        print("\nMemberProfileView GET 요청 시 프로필 정보 확인")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["profile_image"], "http://example.com/image.jpg"
        )
        self.assertEqual(response.data["member"]["nickname"], "test")
        self.assertEqual(response.data["member"]["introduce"], "introduce")
        self.assertEqual(response.data["member"]["favorite_genre"], ["action"])
