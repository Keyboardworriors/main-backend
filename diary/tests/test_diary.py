from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from diary.models import Diary
from member.models import MemberInfo

User = get_user_model()


class DiaryTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@email.com",
            password="testpassword123",
            provider="test",
            provider_user_id="provider123",
        )
        MemberInfo.objects.create(social_account=self.user, nickname="testuser")
        self.client.force_authenticate(user=self.user)

        self.today = timezone.localdate()
        self.past_date_0 = self.today - timedelta(days=4)
        self.past_date = self.today - timedelta(days=5)
        self.future_date = self.today + timedelta(days=3)

        self.diary = Diary.objects.create(
            member=self.user,
            diary_title="오늘의 일기 test",
            content="오늘은 날씨가 좋다. 신나는 노래를 들으며 나가고 싶다. 기분 좋은 하루다.",
            moods=["기쁨", "설렘"],
            date=self.today,
        )
        self.diary_url = reverse(
            "diary:diary-detail", args=[self.diary.diary_id]
        )

    def test_create_diary(self):
        url = reverse("diary:diary-create")
        payload = {
            "diary_title": "새로운 일기 테스트",
            "content": "이건 테스트입니다. 20자 넘게 작성된 내용으로 테스트하고 있습니다.",
            "moods": ["분노", "좌절"],
            "date": self.past_date_0.strftime("%Y-%m-%d"),
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("diary_id", response.data["data"])

    def test_create_diary_future(self):
        url = reverse("diary:diary-create")
        payload = {
            "diary_title": "미래 일기",
            "content": "미래 날짜에는 일기를 쓰면 안 됩니다. 테스트용입니다.",
            "moods": ["불안", "피곤"],
            "date": self.future_date.strftime("%Y-%m-%d"),
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_diary(self):
        url = reverse("diary:diary-create")
        payload = {
            "diary_title": "중복 일기",
            "content": "중복된 날짜로 일기를 쓰려고 합니다.",
            "moods": ["긴장"],
            "date": self.today.strftime("%Y-%m-%d"),
        }
        self.client.post(url, data=payload, format="json")
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_diary_detail(self):
        response = self.client.get(self.diary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["data"]["diary_id"], str(self.diary.diary_id)
        )

    def test_get_diary_list(self):
        Diary.objects.create(
            member=self.user,
            diary_title="과거 일기",
            content="내용입니다." * 10,
            moods=["기쁨"],
            date=self.today - timedelta(days=1),
        )
        url = reverse("diary:diary-main")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Successfully displayed diary list with date.",
        )
        self.assertGreaterEqual(len(response.data["data"]), 2)

    def test_search_diary(self):
        url = reverse("diary:diary-search")
        payload = {"q": "test"}
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)

    def test_delete_diary(self):
        response = self.client.delete(self.diary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Diary.objects.filter(diary_id=self.diary.diary_id).exists()
        )


class EmotionStatusTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@email.com",
            password="testpassword123",
            provider="test",
            provider_user_id="provider123",
        )
        MemberInfo.objects.create(social_account=self.user, nickname="testuser")
        self.client.force_authenticate(user=self.user)

        self.today = timezone.localdate()
        self.ten_days_ago = self.today - timedelta(days=10)

        Diary.objects.create(
            member=self.user,
            diary_title="최근 일기",
            content="최근 일기 내용",
            moods=["기쁨", "신남"],
            date=self.today,
        )
        Diary.objects.create(
            member=self.user,
            diary_title="오래된 일기",
            content="오래된 일기 내용",
            moods=["우울"],
            date=self.ten_days_ago,
        )

    def test_emotion_status_week(self):
        url = reverse("diary:emotion-status") + "?period=week"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["period"], "week")
        stats = response.data["emotion_stats"]
        self.assertIn("기쁨", stats)
        self.assertIn("신남", stats)
        self.assertNotIn("우울", stats)
