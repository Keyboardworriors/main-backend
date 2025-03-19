import requests
from django.contrib.auth import get_user_model, login
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken

from diary import serializers
from member.models import Member, SocialAccount
from member.serializer import (
    MemberSerializer,
    ProfileSerializer,
    SocialAccountSerializer,
)

User = get_user_model()


class MemberRegister(APIView):
    def get(self, request):
        return Response(status=200)

    def post(self, request):
        nickname = request.data.get("nickname", None)
        introduce = request.data.get("introduce", None)
        favorite_genre = request.data.get("favorite_genre", None)

        if favorite_genre and not isinstance(favorite_genre, list):
            favorite_genre = [favorite_genre]
        email = request.data.get("email")
        social_account = SocialAccount.objects.filter(email=email).first()
        if not social_account:
            return Response({"error": "소셜 계정을 찾을 수 없습니다"}, 400)
        member = self.create_member(
            social_account,
            nickname=nickname,
            introduce=introduce,
            favorite_genre=favorite_genre,
        )
        if isinstance(member, dict):  # serializer.errors가 반환된 경우
            return Response({"errors": member}, status=400)
        social_account.member = member
        social_account.is_registered = True
        social_account.save()
        member_data = {
            "member_id": str(member.member_id),
            "email": member.email,
        }
        login(request, member)
        refresh = RefreshToken.for_user(member)
        return Response(
            {
                "message": "Successfully logined",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": member_data,
            }
        )

    def create_member(
        self, social_account, nickname, introduce, favorite_genre
    ):
        data = {
            "email": social_account.email,  # social_account에서 이메일 가져오기
            "nickname": nickname,
            "introduce": introduce,
            "favorite_genre": favorite_genre,
        }
        serializer = MemberSerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        return serializer.errors


class Login(APIView):
    def post(self, request):
        email = request.data.get("email")
        social_account = SocialAccount.objects.filter(email=email).first()
        if not social_account.member:
            return Response({"error": "회원가입이 필요합니다"}, status=404)
        member = social_account.member
        member_data = {
            "member_id": str(member.member_id),
            "email": member.email,
            "profile_image": social_account.profile_image,
        }

        login(request, member)  # backend 명시적으로 지정 필요 가능성 있음
        refresh = RefreshToken.for_user(member)

        return Response(
            {
                "message": "Successfully logged in",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": member_data,
            },
            status=200,
        )


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"message": "Invalid Token"}, status=400)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully Logout"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class MemberMypageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, member_id):
        social_account = get_object_or_404(SocialAccount, member=member_id)
        serializer = SocialAccountSerializer(social_account)
        return Response(serializer.data, status=200)

    def patch(self, request, member_id):
        member = get_object_or_404(User, member_id=member_id)
        serializer = MemberSerializer(member, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=400)
        serializer.save()
        return Response(serializer.data, status=200)

    def delete(self, request, member_id):
        member = get_object_or_404(User, member_id=member_id)
        member.delete()
        return Response({"message": "Successfully deleted"}, status=200)


class MemberProfileView(APIView):
    def get(self, request, member_id):
        member = get_object_or_404(SocialAccount, member=member_id)
        serializer = ProfileSerializer(member)
        return Response(serializer.data, status=200)
