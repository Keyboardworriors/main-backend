from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from diary.models import Diary
from diary.serializers import DiarySerializer


class DiaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, diary_id=None):
        # 특정 일기 조회
        if diary_id:
            diary = get_object_or_404(Diary, id=diary_id, member=request.user)
            serializer = DiarySerializer(diary)
            return Response({
                'message': 'Successfully retrieved diary.', # 일기 조회 성공 !
                'data': serializer.data
            },  status=status.HTTP_200_OK)

        # 모든 일기 조회 ( 메인페이지 )
        diaries = Diary.objects.filter(member=request.user)
        serializer = DiarySerializer(diaries, many=True)
        return Response({
            'message': 'Successfully retrieved diaries.', # 모든 일기 불러오기 성공 !
            'data': serializer.data
        },  status=status.HTTP_200_OK)