import logging

import google.generativeai as genai
import requests
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from config import settings

# Google API 키 설정 (본인의 키로 변경 필요)
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)

import google.generativeai as genai
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings

# Google API 키 설정 (본인의 키로 변경 필요)
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)

# 로깅 설정
logger = logging.getLogger(__name__)


class GetMoods(APIView):
    def post(self, request):
        logger.info("POST request received for GetMoods")
        content = request.data.get("content")

        # 입력값 검증 (일기 내용이 없거나, 문자열이 아닌 경우)
        if not content or not isinstance(content, str):
            logger.warning("Invalid input data for GetMoods")
            return Response(
                {"error": "Invalid input data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            emotions = self.get_emotions(content)
            if not emotions:
                logger.error("Failed to analyze emotions in GetMoods")
                return Response(
                    {"error": "Failed to analyze emotions."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            moods = [
                mood.strip() for mood in emotions.split(",") if mood.strip()
            ]
            logger.info(f"Successfully analyzed emotions: {moods}")
            if len(moods) < 2:
                raise RuntimeError("At least two emotions must be selected.")

            return Response({"moods": moods}, status=status.HTTP_200_OK)

        except ValueError as e:
            # 감정 키워드를 추출할 수 없을 경우 에러 처리
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Unexpected error occurred in GetMoods: {str(e)}")
            return Response(
                {"error": f"Unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_emotions(self, content):
        # 감정 분석할 일기
        diary = content

        # 프롬프트 작성
        prompt = f"""
        다음은 사용자가 작성한 일기입니다.

        [일기]
        {diary}

        위 일기의 감정을 정확히 네가지 고르고, 감정 외에는 절대 출력하지 마세요.  
        다음 감정 목록에서 선택하세요:
        반드시 목록에 있는 감정만 선택하세요.  
        감정만 출력하고, 다른 문장은 절대로 출력하지 마세요.  
        감정은 아래 형식으로 출력하세요.

        [감정 목록]
        "기쁨", "슬픔", "분노", "불안", "사랑", "두려움", "외로움", "설렘", "짜증", "행복", 
        "후회", "자신감", "좌절", "공포", "흥분", "우울", "희망", "질투", "원망", "감동", 
        "미움", "초조", "만족", "실망", "그리움", "죄책감", "충격", "안도", "긴장", "감사"

        출력 예시:
        기쁨, 상쾌함
        
        만약 일기의 내용이 비정상적이라면 감정 키워드를 추출할 수 없습니다.를 출력하세요.
        """

        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)

            # 응답이 없거나 예상 형식이 아닐 경우
            if (
                not response
                or not hasattr(response, "text")
                or not response.text.strip()
            ):
                raise RuntimeError("No valid response received from the model.")

            emotions = response.text.strip()

            if "감정 키워드를 추출할 수 없습니다." in emotions:
                raise ValueError(
                    "Emotion keywords could not be extracted from the diary."
                )

            return emotions

        except Exception as e:
            logger.error(f"Error during emotion analysis: {str(e)}")
            raise RuntimeError(f"Error during emotion analysis: {str(e)}")


def recommend_music(moods, favorite_genre):
    # 프롬프트 작성
    prompt = f"""
    사용자의 감정은 다음과 같습니다: {', '.join(moods)}
    사용자가 선호하는 음악 장르는 {favorite_genre}입니다.

        아래의 조건을 고려하여 사용자에게 음악을 3곡 추천해주세요 
        사용자의 감정과 선호 장르에 어울릴것
        국내외 대중적인 음악 위주
        감성적인 분위기 또는 감정에 잘 맞는 느낌
        유명한 곡만 추천하지 말고 몰랐던 좋은곡도 포함
        
        각 음악의 제목과 가수만 알려주세요.
        다음과 같은 형식으로만 출력해주세요:
        <제목> - <가수 이름>
        
        예시:
        Spring Day - BTS
        Bad Guy - Billie Eilish
        좋은 날 - 아이유
        
        '제목 - 가수' 같은 설명 문구는 절대 포함하지 말고, 실제 음악 제목과 가수 이름만 출력해주세요.
        목록 형태로 총 3곡만 출력해주세요.
        """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        # 응답이 없거나 예상 형식이 아닐 경우 빈 리스트 반환
        if (
            not response
            or not hasattr(response, "text")
            or not response.text.strip()
        ):
            return []

        generated_text = response.text.strip()
        recommendations = []

        for line in generated_text.splitlines():
            line = line.strip()
            if " - " in line:
                try:
                    title, artist = line.split(" - ", 1)
                    recommendations.append(
                        {"title": title.strip(), "artist": artist.strip()}
                    )
                except ValueError:
                    logger.warning(
                        f"Format error in music recommendation: {line}"
                    )
                    raise ValueError(f"Format error: {line}")

        logger.info(
            f"Music recommendations generated successfully: {recommendations}"
        )
        return recommendations[:3]

    except Exception as e:
        logger.error(f"Error during music recommendation: {str(e)}")
        raise RuntimeError(f"Error during music recommendation: {str(e)}")
