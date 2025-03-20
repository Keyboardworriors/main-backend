from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

import diary
from diary.models import Diary

User = get_user_model()

from django.conf import settings


class DiaryAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        if not settings.configured:
            settings.configure()


class DiaryTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.email = "test@email.com"
        self.password = "password123"
        self.nickname = "testnickname"

        self.user = User.objects.create_user(
            email=self.email, password=self.password, nickname=self.nickname
        )

        self.client.force_authenticate(user=self.user)

        self.diary = Diary.objects.create(
            member=self.user,
            diary_title="오늘의 일기 test",
            content="오늘은 날씨가 무척 좋다. 밖에 나가 신나는 노래를 들으며 자전거르 타고싶다."
            "봄이오니까 뻐근했던 몸도 슬슬 풀리는 기분이다. 기분 좋은 팝송 들으며 나들이 가고싶어진다.",
            moods=["joy", "amusement"],
        )

        self.diary_url = f"/api/diary/{self.diary.diary_id}/"

    def test_create_diary(self):
        payload = {
            "diary_title": "새로운 일기 테스트",
            "content": "테스트가 잘 안되서 너무속상한 상태이다. 어려움을 겪고있어서 너무 힘들고 지친다. 왜이걸 해야하는건가으아아아악 머리가 너무아파 요 우우아가가가",
            "moods": ["angry", "annoyance"],
        }
        response = self.client.post(
            "/api/diary/create/", data=payload, format="json"
        )

        print("서버응답 :", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("diary_id", response.data["data"])
        self.assertEqual(
            response.data["data"]["diary_title"], payload["diary_title"]
        )
        self.assertEqual(response.data["data"]["content"], payload["content"])
        print("🥳 일기 생성 테스트 통과")

    def test_get_diary_detail(self):
        diary_id = str(self.diary.diary_id)
        response = self.client.get(self.diary_url)

        print("🔹 요청한 일기 ID:", diary_id)  # 디버깅용
        print("🔹 서버 응답:", response.data)  # 응답 확인

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["diary_id"], diary_id)
        print("🥳 일기 조회 테스트 통과")

    def test_delete_diary(self):
        response = self.client.delete(self.diary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Diary.objects.count(), 0)
        print("🥳 일기 삭제 테스트 통과 ")

    def test_get_diary_list(self):
        """🔹 전체 일기 목록 조회 테스트"""
        response = self.client.get("/api/diary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("data" in response.data)
        print("🥳 전체 일기 목록 조회 테스트 통과!")

    def test_search_diary(self):
        """일기 검색 테스트"""
        payload = {"q": "test"}
        response = self.client.post(
            "/api/diary/search/", data=payload, format="json"
        )

        # 디버깅용
        print("🔹 서버 응답 상태 코드:", response.status_code)
        print("🔹 서버 응답 데이터:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("data" in response.data)
        print("🥳 일기 검색 테스트 통과!")
