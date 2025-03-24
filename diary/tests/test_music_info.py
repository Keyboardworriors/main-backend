from django.test import TestCase

from diary.views.music_views import get_youtube_info


class TestMusicInfo(TestCase):
    # 받은 리스트로 음악 정보 얻는 테스트
    def test_music_info(self):
        recommendations = [
            {"title": "봄편지", "artist": "아이유"},
            {"title": "like jennie", "artist": "jennie"},
            {"title": "MUTT", "artist": "leon thomas"},
        ]
        for rec in recommendations:
            info = get_youtube_info(rec["title"], rec["artist"])
            print(f"\n🎵 {rec['title']} - {rec['artist']} 검색 결과:")

            self.assertIsNotNone(info, f"{rec['title']} 검색 실패 ❌")
            self.assertIn("videoId", info)
            self.assertIn("title", info)
            self.assertIn("artist", info)
            self.assertIn("thumbnail", info)
            self.assertIn("embedUrl", info)
            print(info)
        print("✅ 모든 음악 정보 가져오기 테스트 통과!")
