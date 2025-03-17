from django.utils import timezone
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from diary.models import Diary
from diary.serializers import DiarySerializer


class DiaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 일기 조회
    def get(self, request, diary_id=None):
        # 요청 날짜 가져오기
        date = request.query_params.get("date", None)
        if date:
            diary = Diary.objects.filter(
                member=request.user.member,
                created_at__date=date,
            ).first()
            # 특정 일기 조회
            if diary_id:
                serializer = DiarySerializer(diary_id)
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
        # 모든 일기 조회 ( 메인페이지 ) -> 쓴 날짜 목록 보내기
        diaries = Diary.objects.filter(member=request.user).values_list(
            "created_at"
        )
        diary_dates = [diary["created_at"].date() for diary in diaries]

        return Response(
            {
                "message": "일기 날짜데이터 불러오기 성공.",
                "data": diary_dates,
            },
            status=status.HTTP_200_OK,
        )

    # # 일기 작성
    # def post(self, request):
    #     serializer = DiarySerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(member=request.user, created_at=timezone.now())
    #         return Response({
    #             'message': 'Successfully created diary.', # 일기 작성 성공
    #             'data': serializer.data
    #         }, status=status.HTTP_201_CREATED
    #             )

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
                    "message": "권한이 없습니다. 본인의 일기만 삭제할 수 있습니다.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        diary.delete()
        return Response(
            {"message": "일기가 성공적으로 삭제 되었습니다."},
            status=status.HTTP_200_OK,
        )
