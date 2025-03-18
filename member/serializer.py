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
    email = serializers.ReadOnlyField()

    class Meta:
        model = Member
        fields = ["email", "nickname", "introduce", "favorite_genre"]

    def validate_nickname(self, value):
        request_member = self.instance
        if (
            Member.objects.filter(nickname=value)
            .exclude(member_id=request_member.member_id)
            .exists()
        ):
            raise serializers.ValidationError("중복된 닉네임입니다.")

        if len(value) > 10:
            raise serializers.ValidationError(
                "닉네임은 10자를 초과할 수 없습니다."
            )
        return value

    def validate_introduce(self, value):
        if len(value) > 25:
            raise serializers.ValidationError(
                "한 줄 소개는 25자 이내로 적어주세요"
            )
        return value

    def update(self, instance, validated_data):
        nickname = validated_data.get("nickname")
        if nickname is not None and nickname != "":
            instance.nickname = nickname

        instance.favorite_genre = validated_data.get(
            "favorite_genre", instance.favorite_genre
        )

        introduce = validated_data.get("introduce")
        if introduce is not None and introduce != "":
            instance.introduce = introduce

        instance.save()
        return instance


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
