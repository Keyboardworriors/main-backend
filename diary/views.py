import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from diary.models import Diary
from diary.serializers import DiarySerializer


class DiaryList(APIView):
    permission_classes = [IsAuthenticated]

    # 메인페이지에서의 일기 조회
    def get(self, request):
        # 일기 날짜 리스트만 조회
        diaries = Diary.objects.filter(member=request.user).values_list(
            "created_at", flat=True
        )
        diary_dates = [diary.date().strftime("%Y-%m-%d") for diary in diaries]

        return Response(
            {
                "message": "일기 날짜 데이터 불러오기 성공.",
                "data": diary_dates,
            },
            status=status.HTTP_200_OK,
        )


class DiaryDetail(APIView):
    permission_classes = [IsAuthenticated]

    # 특정 일기 조회
    def get(self, request, diary_id=None):
        if diary_id:
            diary = get_object_or_404(Diary, id=diary_id, member=request.user)
            serializer = DiarySerializer(diary)
            return Response(
                {
                    "message": "일기 조회 성공.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        # 일기가 없으면 일기 쓰기 안내
        return Response(
            {
                "message": "선택한 날짜에 일기가 없습니다.",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )

    # 특정 일기 삭제
    def delete(self, request, diary_id=None):
        diary = get_object_or_404(Diary, id=diary_id, member=request.user)
        if not diary_id:
            return Response(
                {
                    "error": "invalid_request",
                    "message": "삭제할 diary_id가 필요합니다.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif diary.member != request.user:
            return Response(
                {
                    "error": "forbidden",
                    "message": "권한이 없습니다.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        diary.delete()
        return Response(
            {"message": "Successfully deleted."},
            status=status.HTTP_200_OK,
        )


class DiaryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 일기 작성
    def post(self, request):
        serializer = DiarySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(member=request.user)
            return Response(
                {
                    "message": "Successfully created diary.",  # 일기 작성 성공
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )


class DiaryCustomDateCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 작성일과 저장되는 일기날짜가 다를때
    def post(self, request):
        serializer = DiarySerializer(data=request.data)
        if serializer.is_valid():
            created_at = request.data.get("created_at", None)

            # 날짜 없을때
            if not created_at:
                return Response(
                    {
                        "error": "invalid_request",
                        "message": "작성날짜(created_at)를 입력해주세요.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # 날짜형식 검증 (YYYY-MM-DD)
            try:
                created_date = datetime.datetime.strptime(
                    created_at, "%Y-%m-%d"
                ).date()
            except ValueError:
                return Response(
                    {
                        "error": "invalid_date_format",
                        "meassage": "날짜 형식이 잘못되었습니다. (형식: YYYY-MM-DD)",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 미래 날짜 작성 불가
            today = datetime.date.today()
            if created_date > today:
                return Response(
                    {
                        "error": "future_date_not_allowed",
                        "message": "미래의 날짜에는 일기를 작성할 수 없습니다.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 하루에 한개 작성체크
            if Diary.objects.filter(
                member=request.user, created_at__date=created_date
            ).exists():
                return Response(
                    {
                        "error": "already_exists",
                        "message": "해당 날짜에 이미 일기가 존재합니다.",
                    }
                )

            # 저장
            serializer.save(member=request.user, created_at=created_date)
            return Response(
                {
                    "message": "Successfully created diary.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": "invalid_request", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# 일기 검색
class DiarySearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(
        self,
        request,
    ):
        q = request.data.get("q", "").strip()
        # 검색어 없으면
        if not q:
            return Response(
                {
                    "error": "invalid_request",
                    "message": "검색어(q)를 입력해주세요.",
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
                {"error": "not_found", "message": "검색 결과가 없습니다."},
                status=status.HTTP_200_OK,
            )

        serializer = DiarySerializer(diaries, many=True)

        return Response(
            {"message": "일기 검색 성공", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


#
