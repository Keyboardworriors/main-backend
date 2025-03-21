from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import MemberInfo, SocialAccount

User = get_user_model()


class APIViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.social_account = SocialAccount.objects.create(
            provider="kakao",
            provider_user_id="12345",
            email="test@example.com",
            profile_image="http://example.com/image.jpg",
            is_active=False,
        )
        self.member_info = MemberInfo.objects.create(
            social_account=self.social_account,
            nickname="testuser",
            introduce="Hello",
            favorite_genre=["Action"],
        )

    def test_create_member_info_get(self):
        response = self.client.get(reverse("member:member_info_register"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_member_info_post(self):
        data = {
            "email": "test@example.com",
            "nickname": "newuser",
            "introduce": "New intro",
            "favorite_genre": ["Comedy"],
        }
        response = self.client.post(
            reverse("member:member_info_register"), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertTrue(
            SocialAccount.objects.get(email="test@example.com").is_active
        )

    def test_login(self):
        self.social_account.is_active = True
        self.social_account.save()
        data = {"email": "test@example.com"}
        response = self.client.post(reverse("member:login"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

    def test_logout(self):
        refresh = RefreshToken.for_user(self.social_account)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        response = self.client.post(
            reverse("member:logout"), {"refresh_token": str(refresh)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_mypage_get(self):
        self.client.force_authenticate(user=self.social_account)
        response = self.client.get(reverse("member:mypage"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")

    def test_member_mypage_patch(self):
        self.client.force_authenticate(user=self.social_account)
        data = {"nickname": "updated_nick", "favorite_genre": ["Drama"]}
        response = self.client.patch(reverse("member:mypage"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "updated_nick")

    def test_member_mypage_delete(self):
        self.client.force_authenticate(user=self.social_account)
        response = self.client.delete(reverse("member:mypage"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            SocialAccount.objects.filter(email="test@example.com").exists()
        )

    def test_member_profile_get(self):
        self.client.force_authenticate(user=self.social_account)
        response = self.client.get(
            reverse("member:profile", kwargs={"member_id": self.member_info.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "testuser")
