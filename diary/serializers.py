from rest_framework import serializers

from diary.models import Diary


class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = [
            "diary_id",
            "moods",
            "content",
            "rec_music",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["diary_id", "created_at", "updated_at"]

    # content (일기내용) 필드의 길이 제한 검증 추가
    def validate_content(self, value):
        if len(value) > 20:
            raise serializers.ValidationError(
                "일기 내용은 최소 20자 이상 입력해야 합니다."
            )
