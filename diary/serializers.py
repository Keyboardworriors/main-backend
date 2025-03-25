import datetime

from rest_framework import serializers

from diary.models import Diary, Music
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
                    "날짜 형식이 잘못되었습니다. (형식: YYYY-MM-DD)"
                )
        # datetime 으로 들어왔을 경우도 date() 처리 추가
        if isinstance(diary_date, datetime.datetime):
            diary_date = diary_date.date()

        # date 인지 최종확인
        if not isinstance(diary_date, datetime.date):
            raise serializers.ValidationError("날짜 형식이 올바르지 않습니다.")

        data["date"] = diary_date  # DB에 받은 날짜 반영

        # 미래 날짜 방지(작성 불가)
        if diary_date > today:
            raise serializers.ValidationError(
                "미래의 날짜에는 일기를 작성할 수 없습니다."
            )

        # 중복 일기 방지 (하루 한개만 작성 가능)
        if Diary.objects.filter(member=request.user, date=diary_date).exists():
            raise serializers.ValidationError(
                "해당 날짜에 이미 일기가 존재합니다."
            )

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
        fields = ["video_id", "title", "artist", "thumbnail", "embedUrl"]
        read_only_fields = [
            "video_id",
            "title",
            "artist",
            "thumbnail",
            "embedUrl",
        ]


class FavoriteGenreSerializer(serializers.Serializer):
    moods = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )
    favorite_genre = serializers.ListField(
        required=False, allow_null=True, allow_empty=True
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
