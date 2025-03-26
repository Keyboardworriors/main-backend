from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from member.models import MemberInfo

User = get_user_model()


class EmotionMusicAITests(APITestCase):
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

    def test_extract_emotions_from_diary(self):
        """AI로 일기 내용을 분석해 감정 키워드 추출"""
        diary_content = {
            "content": "공부하면서 머리를 너무 많이 썼더니 머리가 시끄럽다. 스트레스 받을때는 역시 조용하고 차분하게 커피 한잔 하면서 창밖을 보는것,,, 오늘까지 빡세게 공부하고 내일은 날씨도 좋은데 밖에나가 놀아야겟다 "
        }
        response = self.client.post(
            "/api/diary/recommendation-keyword/",
            data=diary_content,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("moods", response.data)
        self.assertIsInstance(response.data["moods"], list)
        self.assertGreaterEqual(len(response.data["moods"]), 1)
        print("감정 키워드:", response.data)
        print("감정 키워드 추출 테스트 통과")

    def test_recommend_music_based_on_emotions(
        self,
    ):
        """감정 + 장르 기반 음악 추천 테스트"""
        data = {"moods": ["행복", "희열"], "favorite_genre": ["pop"]}
        response = self.client.post(
            "/api/diary/music/recommend/", data=data, format="json"
        )
        print(data["moods"], data["favorite_genre"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)
        self.assertIsInstance(response.data["data"], list)

        if response.data["data"]:  # 리스트가 비어있지 않으면 체크
            first_music = response.data["data"][0]
            self.assertIn("title", first_music)
            self.assertIn("artist", first_music)
            self.assertIn("video_id", first_music)
            self.assertIn("embedUrl", first_music)
            print(
                "음악 추천 결과 중 첫번째:",
                first_music["title"],
                first_music["artist"],
            )

        print("음악 추천 테스트 통과")
