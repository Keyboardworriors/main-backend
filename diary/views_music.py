from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from googleapiclient.discovery import build
from ytmusicapi import YTMusic
from rest_framework.response import Response

from diary.models import Music

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
youtube = build('youtube', 'v3', developerKey='YOUTUBE_API_KEY')
ytmusic = YTMusic()

# Music 추천
class MusicRecommendationView(APIView):

    def post(self, request):
        moods = request.data.get("moods", []) # 감정 키워드 리스트
        favorite_genre = request.data.get("favorite_genre", []) # 선호 장르 리스트
        # 감정키워드 없을시
        if not moods :
            return Response({"error":"invalid_request", "message": "감정 키워드가 필요합니다."},
                            status=status.HTTP_400_BAD_REQUEST)

        search_query = " ".join(moods + ["음악"] + favorite_genre)#moods keywords + genre 조합으로 검색

        # YouTube Data API(공식) 에서 감정 키워드 기반으로 검색
        search_results = youtube.search().list(
            part="snippet",
            q=search_query,
            type="video",
            maxResults=3,
        ).execute()

        if "items" not in search_results or not search_results["items"]:
            return Response({
                "error": "not_found", "message": "검색 결과가 없습니다."
            },status=status.HTTP_404_NOT_FOUND)

        recommendations = [] # 추천음악목록 저장

        # 검색된 videoId 를 통해 ytmusic api(비공식) 로 추가정보 가져오기
        for item in search_results["items"]:
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]
            thumbnail = item["snippet"]["thumbnails"]["high"]["url"]
            url = f"https://www.youtube.com/watch?v={video_id}"

            # ytmusic API 에서 실제 아티스트 정보 가져오기
            music_info = ytmusic.get_song(video_id)
            artist = music_info.get("videoDetails", {}).get("author", channel)  # 아티스트 정보 가져오기, 없으면 채널명

            # 데이터베이스에 존재하는지 확인 (중복 저장 방지)
            music_obj, created = Music.objects.get_or_create(
                videoId=video_id,
                defaults={
                    "title": title,
                    "artist": artist,
                    "thumbnail": thumbnail,
                    "embedUrl": url,
                }
            )
            recommendations.append({
                "videoId": video_id,
                "title": title,
                "artist": artist,
                "thumbnail": thumbnail,
                "embedUrl": url
            })
        return Response({
            "message": "음악 추천 성공", "rec_music": recommendations},
            status=status.HTTP_200_OK
        )