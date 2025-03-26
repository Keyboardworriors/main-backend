from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
    try:
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
                "title": title,
                "artist": artist,  # AI가 준 아티스트, 제목 그대로 사용
                "thumbnail": snippet["thumbnails"]["high"]["url"],
                "embedUrl": f"https://www.youtube.com/watch?v={video_id}",
            }
        return None
    except Exception as e:
        # 유튜브 API 호출이나 응답 처리 중에 에러 발생 시
        return {
            "error": f"Error occurred while fetching YouTube info: {str(e)}"
        }


class MusicRecommendView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="추천된 음악 목록을 반환합니다. 감정과 선호 장르에 맞는 음악을 추천하고, YouTube 링크를 제공합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "moods": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="사용자가 입력한 감정 목록",
                ),
                "favorite_genre": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="사용자가 선호하는 음악 장르 (optional)",
                ),
            },
            required=["moods", "favorite_genre"],
        ),
        responses={
            200: openapi.Response(
                description="음악 추천 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, description="결과 메시지"
                        ),
                        "data": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "video_id": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="YouTube 비디오 ID",
                                    ),
                                    "title": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="곡 제목",
                                    ),
                                    "artist": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="아티스트 이름",
                                    ),
                                    "thumbnail": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="곡 썸네일 URL",
                                    ),
                                    "embedUrl": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="YouTube 임베드 URL",
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            ),
            404: openapi.Response(description="추천된 음악이 없음"),
            500: openapi.Response(description="서버 에러"),
        },
    )
    # 추천된 음악 정보 리스트 반환
    def post(self, request):
        try:
            serializer = FavoriteGenreSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            moods = serializer.validated_data["moods"]
            favorite_genre = serializer.validated_data["favorite_genre"]

            # ai 기반 음악 추천
            recommendations = recommend_music(moods, favorite_genre)
            results = []
            for rec in recommendations:
                info = get_youtube_info(rec["title"], rec["artist"])
                if info:
                    results.append(info)

                for rec in recommendations:
                    # get_youtube_info 호출 예외 처리
                    info = get_youtube_info(rec["title"], rec["artist"])
                    if info and "error" not in info:
                        results.append(info)
                    else:
                        results.append(
                            {
                                "error": f"Failed to get YouTube info for {rec['title']}"
                            }
                        )

                return Response(
                    {
                        "message": "Music recommendation completed.",
                        "data": results,
                    },
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {"error": f"Unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
