import json
from xml.dom import ValidationErr

from rest_framework import serializers

from member.models import MemberInfo, SocialAccount


class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ["email", "provider", "provider_user_id", "profile_image"]

    def validated_email(self, value):
        if not value:
            raise serializers.ValidationError(
                "Please provide an email address."
            )
        elif SocialAccount.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email address is already in use."
            )


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
            raise serializers.ValidationError("This nickname is already taken.")

        if len(value.encode("utf-8")) > 15:
            raise serializers.ValidationError(
                "Nickname can be up to 15 characters (Korean)."
            )
        return value

    def validate_introduce(self, value):
        if value and len(value) > 25:
            raise serializers.ValidationError(
                "Introduce can be up to 25 characters."
            )
        return value

    def validate_favorite_genre(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid format.")
        elif not isinstance(value, list):
            raise serializers.ValidationError("favorite_genre must be a list.")
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
            validated_data.get(
                "favorite_genre",
            )
        )
        new_member = MemberInfo.objects.create(**validated_data)
        return new_member


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


class SocialAccountInfoSerializer(serializers.Serializer):
    provider = serializers.CharField()
    provider_user_id = serializers.CharField()
    email = serializers.EmailField()
    profile_image = serializers.URLField(allow_blank=True)
    is_active = serializers.BooleanField()

    def validate_provide(self, value):
        if value not in ["kakao", "naver"]:
            raise serializers.ValidationError("Invalid provider")
        return value

    def validate_email(self, value):
        if value is None:
            raise serializers.ValidationError("Invalid email")
        return value
