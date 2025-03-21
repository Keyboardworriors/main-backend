import json
from rest_framework import serializers
from member.models import SocialAccount, MemberInfo


class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ["email", "provider", "provider_user_id", "profile_image"]


class MemberInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberInfo
        fields = ["nickname", "introduce", "favorite_genre", "social_account"]

    def validate_nickname(self, value):
        if (
            self.instance
            and MemberInfo.objects.filter(nickname=value)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise serializers.ValidationError("중복된 닉네임입니다.")

        if len(value.encode("utf-8")) > 30:
            raise serializers.ValidationError("닉네임은 한글 기준으로 최대 15자까지 입력할 수 있습니다.")
        return value

    def validate_introduce(self, value):
        if value and len(value) > 25:
            raise serializers.ValidationError("한 줄 소개는 25자 이내로 적어주세요.")
        return value

    def validate_favorite_genre(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("올바른 형식이 아닙니다.")
        elif not isinstance(value, list):
            raise serializers.ValidationError("favorite_genre는 리스트 형식이어야 합니다.")
        return value or []

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get("nickname", instance.nickname)
        instance.introduce = validated_data.get("introduce", instance.introduce)
        instance.favorite_genre = self.validate_favorite_genre(
            validated_data.get("favorite_genre", instance.favorite_genre)
        )

        instance.save()
        return instance

    def create(self, validated_data):
        validated_data["favorite_genre"] = self.validate_favorite_genre(
            validated_data.get("favorite_genre", [])
        )
        return MemberInfo.objects.create(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = MemberInfo
        fields = ["profile_image", "member"]
        depth = 1

    def get_member(self, obj):
        return {
            "introduce": obj.introduce,
            "nickname": obj.nickname,
            "favorite_genre": obj.favorite_genre,
        }

    def get_profile_image(self, obj):
        return obj.social_account.profile_image if obj.social_account else None
