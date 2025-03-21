from django.conf import settings
from googleapiclient.discovery import build
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ytmusicapi import YTMusic

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
youtube = build("youtube", "v3", developerKey="YOUTUBE_API_KEY")
ytmusic = YTMusic()


# Genai 통해 받은 음악 리스트를 유튜브에 검색해 정보 반환
def get_youtube_info(title,artist):
    query = f'{title} {artist} official' # 검색어 설정
    search_results = ytmusic.search(query=query,filter="songs", limit=1)

    if not search_results:
        return None

    music = search_results[0]
    return {
        "videoId": music["videoId"],
        "title": music["title"],
        "artist": music["artists"][0]["name"] if "artists" in music else "Unknown",
        "thumbnail": music["thumbnails"][-1]["url"],  # 가장 고화질 썸네일
        "embedUrl": f"https://www.youtube.com/embed/{music['videoId']}",
    }

class MusicRedommendView(APIView):
    # 추천된 음악 정보 리스트 반환
    def post(self,request):
        recommendations = request.data.get('recommendations',[])

        results = []
        for rec in recommendations:
            info = get_youtube_info(rec["title"],rec["artist"])
            if info:
                results.append(info)

        return Response({
            "message": "음악 추천 완료", "data": results}, status=status.HTTP_200_OK
        )
