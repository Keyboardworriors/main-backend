import datetime

from google.generativeai.types import to_file_data
from rest_framework import serializers, status

from diary.models import Diary, Music


class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = [
            "diary_id",
            "member",
            "moods",
            "diary_title",
            "content",
            "rec_music",
            "created_at",
        ]
        read_only_fields = ["diary_id", "member"]

    def validate(self, data):
        request = self.context.get("request")
        today = datetime.date.today()

        # 원본 요청 데이터에서 가져오기!!
        created_at = self.initial_data.get("created_at", today)

        # None 값 처리
        if created_at is None:
            created_at = today

        # 날짜형식 검증 : 문자열이면 변환
        if isinstance(created_at, str):
            try:
                created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d").date()
            except ValueError:
                raise serializers.ValidationError(
                    "날짜 형식이 잘못되었습니다. (형식: YYYY-MM-DD)"
                )

        data["created_at"] = created_at # 데이터에 created_at 반영

        # 미래 날짜 방지(작성 불가)
        if created_at > today:
            raise serializers.ValidationError("미래의 날짜에는 일기를 작성할 수 없습니다.")

        # 중복 일기 방지 (하루 한개만 작성가능
        if Diary.objects.filter(member=request.user,created_at__date=created_at).exists():
            raise serializers.ValidationError("해당 날짜에 이미 일기가 존재합니다.")

        return data

    # content (일기내용) 필드의 길이 제한 검증 추가
    def validate_content(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("일기 내용을 입력해야 합니다.")
        if len(value) < 20:
            raise serializers.ValidationError(
                "일기 내용은 최소 20자 이상 입력해야 합니다."
            )
        return value

class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = ["videoId", "title", "artist", "thumbnail", "embedUrl"]
        read_only_fields = [
            "videoId",
            "title",
            "artist",
            "thumbnail",
            "embedUrl",
        ]
