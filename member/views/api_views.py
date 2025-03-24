import copy

import requests
from django.contrib.auth import get_user_model, login
from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import MemberInfo, SocialAccount
from member.serializer import (
    MemberInfoSerializer,
    ProfileSerializer,
    SocialAccountSerializer,
)

User = get_user_model()


class CreateMemberInfo(APIView):
    def get(self, request):
        return Response(status=200)

    def post(self, request):
        email = request.data.get("email")
        social_account = SocialAccount.objects.filter(email=email).first()
        if not social_account:
            return Response({"error": "소셜 계정을 찾을 수 없습니다"}, 400)
        data = copy.deepcopy(request.data)
        data["social_account"] = str(social_account)

        serializer = MemberInfoSerializer(data=data)
        if serializer.is_valid():
            social_account.is_active = True
            social_account.save()
            serializer.save()

            refresh = RefreshToken.for_user(social_account)
            return Response(
                {
                    "message": "Successfully logined",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": {
                        "email": email,
                        "profile_image": social_account.profile_image,
                        "nickname": serializer.data["nickname"],
                        "introduce": serializer.data.get("introduce"),
                        "favorite_genre": serializer.data.get("favorite_genre"),
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=400)

    def create_member_info(
        self, social_account, nickname, introduce, favorite_genre
    ):
        data = {
            "nickname": nickname,
            "introduce": introduce,
            "favorite_genre": favorite_genre,
            "social_account": social_account,
        }
        serializer = MemberInfoSerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        return serializer.errors


class Login(APIView):
    def post(self, request):
        email = request.data.get("email")
        if email is None:
            return Response({"error": "Invalid eamil"}, 400)
        member_info = MemberInfo.objects.filter(
            social_account__email=email
        ).first()

        if not member_info.social_account.is_active:
            return Response(
                {"error": "회원 정보 등록이 필요합니다"}, status=404
            )
        member_data = {
            "social_account": member_info.social_account,
            "nickname": member_info.nickname,
        }
        refresh = RefreshToken.for_user(member_info.social_account)
        social_account_serializer = SocialAccountSerializer(
            member_info.social_account
        )

        return Response(
            {
                "message": "Successfully logged in",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": {
                    "email": social_account_serializer.data.get("email"),
                    "profile_image": social_account_serializer.data.get(
                        "profile_image"
                    ),
                    "nickname": member_info.nickname,
                },
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

    def get(self, request):
        member_info = MemberInfo.objects.filter(
            social_account=request.user
        ).first()
        if not member_info:
            return Response({"error": "Member info not found"}, status=404)

        serializer = MemberInfoSerializer(member_info)
        return Response(serializer.data, status=200)

    def patch(self, request):
        social_account = request.user
        member_info = MemberInfo.objects.filter(
            social_account=social_account
        ).first()
        serializer = MemberInfoSerializer(
            member_info, data=request.data, partial=True
        )

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=400)
        serializer.save()
        return Response(serializer.data, status=200)

    def delete(self, request):
        social_account = request.user

        social_account.delete()
        return Response({"message": "Successfully deleted"}, status=200)


class MemberProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        member_info = MemberInfo.objects.filter(
            social_account=request.user
        ).first()
        serializer = ProfileSerializer(member_info)
        return Response(serializer.data, status=200)
