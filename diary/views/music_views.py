import logging

from django.conf import settings
from googleapiclient.discovery import build
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from diary.serializers import FavoriteGenreSerializer
from diary.views.ai_views import recommend_music

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def get_youtube_info(title, artist):
    try:
        logger.info(f"Fetching YouTube info for {title} - {artist}")
        query = f"{title} {artist} official"
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
            logger.debug(f"Successfully fetched YouTube info for {title}")
            return {
                "video_id": video_id,
                "title": title,
                "artist": artist,
                "thumbnail": snippet["thumbnails"]["high"]["url"],
                "embedUrl": f"https://www.youtube.com/watch?v={video_id}",
            }
        logger.warning(f"No YouTube results found for {title} - {artist}")
        return None
    except Exception as e:
        logger.error(f"YouTube API error for {title}: {str(e)}", exc_info=True)
        return {
            "error": f"Error occurred while fetching YouTube info: {str(e)}"
        }


class MusicRecommendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Music recommendation request from user {request.user.id}")
        try:
            serializer = FavoriteGenreSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            logger.debug("Input data validation successful")

            moods = serializer.validated_data["moods"]
            favorite_genre = serializer.validated_data["favorite_genre"]
            logger.info(
                f"Processing request - Moods: {moods}, Genre: {favorite_genre}"
            )

            recommendations = recommend_music(moods, favorite_genre)
            logger.info(
                f"Received {len(recommendations)} recommendations from AI"
            )

            results = []

            for rec in recommendations:
                logger.debug(f"Processing recommendation: {rec['title']}")
                info = get_youtube_info(rec["title"], rec["artist"])

                if info and "error" not in info:
                    results.append(info)
                    logger.debug(f"Added YouTube info for {rec['title']}")
                else:
                    error_msg = info.get("error") if info else "No YouTube data"
                    logger.warning(
                        f"Failed to process {rec['title']}: {error_msg}"
                    )
                    results.append(
                        {
                            "error": f"Failed to get YouTube info for {rec['title']}"
                        }
                    )

            logger.info(f"Successfully processed {len(results)} tracks")
            return Response(
                {
                    "message": "Music recommendation completed.",
                    "data": results,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Recommendation failed: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
