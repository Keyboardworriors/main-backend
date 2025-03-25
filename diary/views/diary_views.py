import datetime
from collections import Counter

from django.db.models import Q
from django.utils.timezone import now
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from diary.models import Diary
from diary.serializers import DiarySerializer


class DiaryListView(APIView):
    permission_classes = [IsAuthenticated]

    # 메인페이지에서의 일기 조회
    def get(self, request):
        # 일기 날짜
        all_diary = Diary.objects.filter(
            member=request.user.social_account_id
        ).values("diary_id", "created_at")
        diary_data = [
            {
                "date": diary["created_at"].strftime("%Y-%m-%d"),
                "diary_id": str(diary["diary_id"]),
            }
            for diary in all_diary
        ]

        return Response(
            {
                "message": "Successfully displayed diary list with date.",
                "data": diary_data,
            },
            status=status.HTTP_200_OK,
        )


class DiaryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # 특정 일기 조회
    def get(self, request, diary_id):
        if diary_id:
            diary = get_object_or_404(
                Diary, diary_id=diary_id, member=request.user.social_account_id
            )
            serializer = DiarySerializer(diary)
            return Response(
                {
                    "message": "Successfully diary detail.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        # 일기가 없으면 일기 쓰기 안내
        return Response(
            {
                "message": "No diary for the selected date",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )

    # 특정 일기 삭제
    def delete(self, request, diary_id):
        diary = get_object_or_404(
            Diary, diary_id=diary_id, member=request.user.social_account_id
        )

        diary.delete()
        return Response(
            {"message": "Successfully deleted."},  # 일기 삭제 성공
            status=status.HTTP_200_OK,
        )


# 일기 작성
class DiaryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DiarySerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            created_at = request.data.get("created_at", datetime.date.today())
            serializer.save(member=request.user, created_at=created_at)
            return Response(
                {
                    "message": "Successfully created diary.",  # 일기 작성 성공
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        # 유효성 검증 실패 시 예외 처리 추가
        return Response(
            {"error": "invalid_request", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# 일기 검색
class DiarySearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        q = request.data.get("q", "").strip()
        # 검색어 없으면
        if not q:
            return Response(
                {
                    "error": "invalid_request",
                    "message": "input search query(q).",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 제목, 내용 에서 검색
        diaries = Diary.objects.filter(
            Q(diary_title__icontains=q) | Q(content__icontains=q),
            member=request.user,
        ).order_by("-created_at")

        # 검색 데이터 없을 때
        if not diaries.exists():
            return Response(
                {"error": "not_found", "message": "not found for your search."},
                status=status.HTTP_200_OK,
            )

        serializer = DiarySerializer(diaries, many=True)

        return Response(
            {"message": "Successfully searched diary", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


# 기간별 감정 통계
class EmotionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.GET.get("period")
        today = now().date()

        if period == "week":
            start_date = today - datetime.timedelta(days=7)
        elif period == "month":
            start_date = today - datetime.timedelta(days=30)
        elif period == "year":
            start_date = today - datetime.timedelta(days=365)
        else:
            return Response(
                {"error": "Please use one of: week, month, or year."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 해당 기간의 다이어리 조회
        all_diary = Diary.objects.filter(
            member=request.user.social_account_id,
            date__gte=start_date,
            date__lte=today,
        )

        # 감정 키워드 수집
        all_moods = []
        for diary in all_diary:
            all_moods.extend(diary.moods)

        mood_counts = Counter(all_moods)

        return Response(
            {
                "period": period,
                "start_date": start_date,
                "end_date": today,
                "emotion_stats": mood_counts,
            },
            status=status.HTTP_200_OK,
        )
