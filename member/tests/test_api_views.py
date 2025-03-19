from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import Member, SocialAccount

User = get_user_model()


class MemberViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            nickname="testuser",
            password="testpass123",
            favorite_genre=["Action"],
        )
        self.social_account = SocialAccount.objects.create(
            provider="kakao",
            provider_user_id="12345",
            email="test@example.com",
            member=self.user,
            profile_image="http://example.com/image.jpg",
            is_registered=True,
        )

    def test_member_register_get(self):
        response = self.client.get(reverse("member:register"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_register_post(self):
        data = {
            "email": "new@example.com",
            "nickname": "newuser",
            "introduce": "Hello",
            "favorite_genre": ["Action", "Comedy"],
        }
        SocialAccount.objects.create(
            email="new@example.com", provider="kakao", provider_user_id="67890"
        )

        response = self.client.post(reverse("member:register"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)
        self.assertIn("refresh_token", response.data)

    def test_login(self):
        data = {"email": "test@example.com"}
        response = self.client.post(reverse("member:login"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.data)

    @patch("rest_framework_simplejwt.tokens.RefreshToken.blacklist")
    def test_logout(self, mock_blacklist):
        self.client.force_authenticate(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            reverse("member:logout"), {"refresh_token": str(refresh)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_blacklist.assert_called_once()

    def test_member_mypage_get(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("member:mypage", kwargs={"member_id": self.user.member_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")

    def test_member_mypage_patch(self):
        self.client.force_authenticate(user=self.user)
        data = {"nickname": "updated_nick", "favorite_genre": ["Drama"]}
        response = self.client.patch(
            reverse("member:mypage", kwargs={"member_id": self.user.member_id}),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], "updated_nick")

    def test_member_mypage_delete(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse("member:mypage", kwargs={"member_id": self.user.member_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            User.objects.filter(member_id=self.user.member_id).exists()
        )

    def test_member_profile_get(self):
        response = self.client.get(
            reverse("member:profile", kwargs={"member_id": self.user.member_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["member"]["nickname"], "testuser")
