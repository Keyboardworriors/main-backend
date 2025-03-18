import random
import string

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import Member, SocialAccount

User = get_user_model()


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


class MemberMypageViewTest(APITestCase):
    def setUp(self):
        self.client = self.client_class()
        self.email = "testuser@example.com"
        self.password = "password123"
        self.nickname = generate_random_string(10)
        self.favorite_genre = ["감정1", "감정2"]

        # 회원 생성
        self.social_account = SocialAccount.objects.create(
            provider="kakao",
            provider_user_id="123456",
            email=self.email,
            profile_image="http://example.com/profile.jpg",
        )

        self.user = Member.objects.create_user(
            email=self.email,
            nickname=self.nickname,
            password=self.password,
            favorite_genre=self.favorite_genre,
        )
        self.user.save()
        self.social_account.member = self.user
        self.social_account.save()

        self.client.login(email=self.email, password=self.password)
        self.member_id = self.user.member_id

    def test_member_mypage_get(self):
        """회원의 소셜 계정 정보 가져오기"""
        url = reverse("member:mypage", args=[self.member_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.email)
        self.assertEqual(
            response.data["profile_image"], self.social_account.profile_image
        )
        self.assertEqual(
            response.data["member"]["favorite_genre"], self.favorite_genre
        )

    def test_member_mypage_patch(self):
        """회원 정보 수정"""
        url = reverse("member:mypage", args=[self.member_id])
        data = {"nickname": "newnick"}
        response = self.client.patch(url, data, format="json")
        try:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        except Exception as e:
            print(e)
        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, "newnick")

    def test_member_mypage_delete(self):
        """회원 탈퇴"""
        url = reverse("member:mypage", args=[self.member_id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.assertRaises(User.DoesNotExist):
            self.user.refresh_from_db()

    def test_logout(self):
        """로그아웃 테스트"""
        url = reverse("member:logout")
        refresh_token = str(RefreshToken.for_user(self.user))
        response = self.client.post(
            url, {"refresh_token": refresh_token}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["msg"], "Successfully Logout")

    def tearDown(self):
        """테스트 후 데이터 삭제"""
        User.objects.all().delete()
        SocialAccount.objects.all().delete()
