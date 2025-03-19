import json

from rest_framework import serializers

from member.models import Member, SocialAccount


class SocialAccountSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()

    class Meta:
        model = SocialAccount
        fields = ["email", "member", "profile_image"]

    def get_member(self, obj):
        return {
            "nickname": obj.member.nickname,
            "introduce": obj.member.introduce,
            "favorite_genre": obj.member.favorite_genre,
        }


class MemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = Member
        fields = ["email", "nickname", "introduce", "favorite_genre"]

    def validate(self, attrs):
        if "email" not in attrs:
            raise serializers.ValidationError("Email is required")
        return attrs

    def validate_nickname(self, value):
        if (
            self.instance
            and Member.objects.filter(nickname=value)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise serializers.ValidationError("중복된 닉네임입니다.")

        if len(value.encode("utf-8")) > 30:
            raise serializers.ValidationError(
                "닉네임은 한글 기준으로 최대 15자까지 입력할 수 있습니다."
            )
        return value

    def validate_introduce(self, value):
        if len(value) > 25:
            raise serializers.ValidationError(
                "한 줄 소개는 25자 이내로 적어주세요"
            )
        return value

    def validate_favorite_genre(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("올바른 형식이 아닙니다.")
        elif not isinstance(value, list):
            value = [value]
        return value or []

    def update(self, instance, validated_data):
        nickname = validated_data.get("nickname")
        if nickname is not None and nickname != "":
            instance.nickname = nickname

        instance.favorite_genre = self.validate_favorite_genre(
            validated_data.get("favorite_genre", instance.favorite_genre)
        )

        introduce = validated_data.get("introduce")
        if introduce is not None and introduce != "":
            instance.introduce = introduce

        instance.save()
        return instance

    def create(self, validated_data):
        validated_data["favorite_genre"] = self.validate_favorite_genre(
            validated_data.get("favorite_genre", [])
        )
        return Member.objects.create_user(
            email=validated_data["email"],  # 명시적으로 email 전달
            nickname=validated_data.get("nickname", ""),
            introduce=validated_data.get("introduce", ""),
            favorite_genre=validated_data.get("favorite_genre", []),
        )


class ProfileSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()

    class Meta:
        model = SocialAccount
        fields = ["profile_image", "member"]

    def get_member(self, obj):
        return {
            "introduce": obj.member.introduce,
            "nickname": obj.member.nickname,
            "favorite_genre": obj.member.favorite_genre,
        }
