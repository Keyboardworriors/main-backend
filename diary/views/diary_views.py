import datetime
import logging
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

logger = logging.getLogger(__name__)


class DiaryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(
            "Retrieving diary list for user %s", request.user.social_account_id
        )
        all_diary = Diary.objects.filter(
            member=request.user.social_account_id
        ).values("diary_id", "date")
        diary_data = [
            {
                "date": diary["date"].strftime("%Y-%m-%d"),
                "diary_id": str(diary["diary_id"]),
            }
            for diary in all_diary
        ]
        logger.info("Successfully retrieved %d diaries", len(diary_data))
        return Response(
            {
                "message": "Successfully displayed diary list with date.",
                "data": diary_data,
            },
            status=status.HTTP_200_OK,
        )


class DiaryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, diary_id):
        logger.info("Retrieving diary detail for diary_id %s", diary_id)
        if diary_id:
            diary = get_object_or_404(
                Diary, diary_id=diary_id, member=request.user.social_account_id
            )
            serializer = DiarySerializer(diary)
            logger.info("Successfully retrieved diary detail")
            return Response(
                {
                    "message": "Successfully diary detail.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        logger.info("No diary found for the selected date")
        return Response(
            {
                "message": "No diary for the selected date",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, diary_id):
        logger.info("Deleting diary with id %s", diary_id)
        diary = get_object_or_404(
            Diary, diary_id=diary_id, member=request.user.social_account_id
        )
        diary.delete()
        logger.info("Successfully deleted diary")
        return Response(
            {"message": "Successfully deleted."},
            status=status.HTTP_200_OK,
        )


class DiaryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(
            "Creating new diary for user %s", request.user.social_account_id
        )
        serializer = DiarySerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            created_at = request.data.get("created_at", datetime.date.today())
            serializer.save(member=request.user, created_at=created_at)
            logger.info("Successfully created diary")
            return Response(
                {
                    "message": "Successfully created diary.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        logger.warning("Invalid diary data: %s", serializer.errors)
        return Response(
            {"error": "invalid_request", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DiarySearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        q = request.data.get("q", "").strip()
        logger.info(
            "Searching diaries for user %s with query: %s",
            request.user.social_account_id,
            q,
        )
        if not q:
            logger.warning("Empty search query")
            return Response(
                {
                    "error": "invalid_request",
                    "message": "input search query(q).",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        diaries = Diary.objects.filter(
            Q(diary_title__icontains=q) | Q(content__icontains=q),
            member=request.user,
        ).order_by("-created_at")

        if not diaries.exists():
            logger.info("No diaries found for search query")
            return Response(
                {"error": "not_found", "message": "not found for your search."},
                status=status.HTTP_200_OK,
            )

        serializer = DiarySerializer(diaries, many=True)
        logger.info(
            "Successfully searched diaries, found %d results", len(diaries)
        )
        return Response(
            {"message": "Successfully searched diary", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class EmotionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.GET.get("period")
        today = now().date()
        logger.info(
            "Retrieving emotion status for user %s, period: %s",
            request.user.social_account_id,
            period,
        )

        if period == "week":
            start_date = today - datetime.timedelta(days=7)
        elif period == "month":
            start_date = today - datetime.timedelta(days=30)
        elif period == "year":
            start_date = today - datetime.timedelta(days=365)
        else:
            logger.warning("Invalid period specified: %s", period)
            return Response(
                {"error": "Please use one of: week, month, or year."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        all_diary = Diary.objects.filter(
            member=request.user.social_account_id,
            date__gte=start_date,
            date__lte=today,
        )

        all_moods = []
        for diary in all_diary:
            all_moods.extend(diary.moods)

        mood_counts = Counter(all_moods)
        logger.info("Successfully retrieved emotion status")
        return Response(
            {
                "period": period,
                "start_date": start_date,
                "end_date": today,
                "emotion_stats": mood_counts,
            },
            status=status.HTTP_200_OK,
        )
