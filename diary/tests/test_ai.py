from rest_framework import status
from rest_framework.test import APITestCase


class EmotionMusicAITests(APITestCase):
    def test_extract_emotions_from_diary(self):
        """일기 내용을 AI로 분석해서 감정 키워드 추출 테스트"""
        diary_content = {
            "content": "공부하면서 머리를 너무 많이 썼더니 머리가 시끄럽다. 스트레스 받을때는 역시 조용하고 차분하게 커피 한잔 하면서 창밖을 보는것,,, 오늘까지 빡세게 공부하고 내일은 날씨도 좋은데 밖에나가 놀아야겟다 "
        }
        response = self.client.post(
            "/api/diary/recommendation-keyword/",
            data=diary_content,
            format="json",
        )

        print("📥 감정 분석 요청:", diary_content)
        print("📤 감정 분석 응답:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("moods", response.data)
        self.assertIsInstance(response.data["moods"], list)
        self.assertGreaterEqual(len(response.data["moods"]), 1)
        print("🥳 감정 키워드 추출 테스트 통과")

    # def test_recommend_music_based_on_emotions(
    #     self,
    # ):
    #     """감정 + 장르 기반 음악 추천 테스트"""
    #     data = {"moods": ["피곤", "초조"], "favorite_genre": "pop"}
    #     response = self.client.post(
    #         "/api/diary/music/recommend/", data=data, format="json"
    #     )
    #
    #     print("📥 음악 추천 요청:", data)
    #     print("📤 음악 추천 응답:", response.data)
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn("data", response.data)
    #     self.assertIsInstance(response.data["data"], list)
    #     self.assertGreaterEqual(len(response.data["data"]), 1)
    #
    #     first_music = response.data["data"][0]
    #     self.assertIn("title", first_music)
    #     self.assertIn("artist", first_music)
    #     self.assertIn("videoId", first_music)
    #     self.assertIn("embedUrl", first_music)
    #
    #     print("🎧 음악 추천 결과:", first_music)
    #     print("🥳 음악 추천 테스트 통과")
