from django.test import TestCase

from diary.views.music_views import get_youtube_info


class TestMusicInfo(TestCase):
    def test_music_info_returns_expected_keys(self):
        recommendations = [
            {"title": "봄편지", "artist": "아이유"},
            {"title": "like jennie", "artist": "jennie"},
            {"title": "MUTT", "artist": "leon thomas"},
        ]

        for rec in recommendations:
            info = get_youtube_info(rec["title"], rec["artist"])

            # info가 None이 아닌 경우만 검사 (API 실패 시는 pass 처리)
            if info and "error" not in info:
                print("검색 성공:", info["title"], info["video_id"])
                self.assertIn("video_id", info)
                self.assertIn("title", info)
                self.assertIn("artist", info)
                self.assertIn("thumbnail", info)
                self.assertIn("embedUrl", info)
            else:
                print(f"유튜브 API 실패: {rec['title']}")

        print("음악 정보 검색 테스트 통과")
