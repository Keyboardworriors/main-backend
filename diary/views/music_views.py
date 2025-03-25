from django.conf import settings
from googleapiclient.discovery import build
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from diary.serializers import FavoriteGenreSerializer
from diary.views.ai_views import recommend_music

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


# Genai 통해 받은 음악 리스트를 유튜브에 검색해 정보 반환
def get_youtube_info(title, artist):
    query = f"{title} {artist} official"  # 검색어 설정
    response = (
        youtube.search()
        .list(
            q=query,
            part="snippet",
            type="video",
            maxResults=1,
        )
        .execute()
    )

    items = response.get("items", [])
    if items:
        video = items[0]
        video_id = video["id"]["videoId"]
        snippet = video["snippet"]
        return {
            "video_id": video_id,
            "title": snippet["title"],
            "artist": artist,  # AI가 준 아티스트로 그대로 사용
            "thumbnail": snippet["thumbnails"]["high"]["url"],
            "embedUrl": f"https://www.youtube.com/watch?v={video_id}",
        }
    return None


class MusicRecommendView(APIView):
    permission_classes = [IsAuthenticated]

    # 추천된 음악 정보 리스트 반환
    def post(self, request):
        serializer = FavoriteGenreSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        moods = serializer.validated_data["moods"]
        favorite_genre = serializer.validated_data.get("favorite_genre", None)

        # ai 기반 음악 추천
        recommendations = recommend_music(moods, favorite_genre)
        results = []
        for rec in recommendations:
            info = get_youtube_info(rec["title"], rec["artist"])
            if info:
                results.append(info)

        return Response(
            {"message": "음악 추천 완료", "data": results},
            status=status.HTTP_200_OK,
        )
