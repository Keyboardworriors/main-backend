import datetime

from rest_framework import serializers

from diary.models import Diary
from member.models import MemberInfo


class DiarySerializer(serializers.ModelSerializer):
    rec_music = serializers.DictField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Diary
        fields = [
            "diary_id",
            "member",
            "moods",
            "diary_title",
            "content",
            "rec_music",
            "date",
            "created_at",
        ]
        read_only_fields = ["diary_id", "member", "created_at"]

    def validate(self, data):
        request = self.context.get("request")
        today = datetime.date.today()

        # 원본 요청 데이터에서 가져오기!!
        diary_date = self.initial_data.get("date", today)

        # None 값 처리
        if diary_date is None:
            diary_date = today

        # 날짜형식 검증 : 문자열이면 변환
        if isinstance(diary_date, str):
            try:
                diary_date = datetime.datetime.strptime(
                    diary_date, "%Y-%m-%d"
                ).date()
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid date format. Use YYYY-MM-DD."
                )
        # datetime 으로 들어왔을 경우도 date() 처리 추가
        if isinstance(diary_date, datetime.datetime):
            diary_date = diary_date.date()

        # date 인지 최종확인
        if not isinstance(diary_date, datetime.date):
            raise serializers.ValidationError("Date format is incorrect.")

        data["date"] = diary_date  # DB에 받은 날짜 반영

        # 미래 날짜 방지(작성 불가)
        if diary_date > today:
            raise serializers.ValidationError(
                "You cannot write a diary for a future date."
            )

        # 중복 일기 방지 (하루 한개만 작성 가능)
        if Diary.objects.filter(member=request.user, date=diary_date).exists():
            raise serializers.ValidationError(
                "A diary already exists for the selected date."
            )

        return data

    def validate_diary_title(self, diary_title):
        if len(diary_title) > 20:
            raise serializers.ValidationError(
                "diary title must be at most 20 characters."
            )
        return diary_title

    # content (일기내용) 필드의 길이 제한 검증 추가
    def validate_content(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Diary content is required.")
        if len(value) < 20:
            raise serializers.ValidationError(
                "Diary content must be at least 20 characters long."
            )
        return value


class FavoriteGenreSerializer(serializers.Serializer):
    moods = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )
    favorite_genre = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        allow_empty=True,
    )

    def validate(self, attrs):
        user = self.context["request"].user
        if "favorite_genre" not in attrs:
            try:
                member_info = MemberInfo.objects.get(social_account=user)
                attrs["favorite_genre"] = member_info.favorite_genre
            except MemberInfo.DoesNotExist:
                pass

        return attrs
