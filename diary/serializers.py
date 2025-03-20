from rest_framework import serializers

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
        read_only_fields = ["diary_id", "member", "created_at"]

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
