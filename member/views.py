import requests
from django.contrib.auth import get_user_model, login
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken

from diary import serializers
from member.models import SocialAccount, Member
from member.serializer import (
    MemberSerializer,
    ProfileSerializer,
    SocialAccountSerializer,
)

User = get_user_model()

class MemberRegister(APIView):
    def get(self,request):
        social_account = request.session.get("social_account")
        try:
            data = {
                "email":social_account["email"],
                "profile_image": social_account["profile_image"]
            }
            return Response(data, status=200)
        except Exception as e:
            return Response({"error":f"{e}"}, status=400)
        finally:
            request.session.pop("social_account_id", None)

    def post(self,request):
        nickname = request.data.get("nickname",None)
        introduce = request.data.get("introduce",None)
        favorite_genre = request.data.get("favorite_genre",None)
        if not isinstance(favorite_genre, list):
            favorite_genre = [favorite_genre]
        email = request.data.get("email")
        social_account = SocialAccount.objects.filter(email=email).first()
        member = self.create_member(
            social_account,
            nickname=nickname,
            introduce=introduce,
            favorite_genre=favorite_genre,
        )
        member_dict = model_to_dict(member)
        login(request, member)
        refresh = RefreshToken.for_user(member)
        return Response(
            {
                "message": "Successfully logined",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": member_dict,
            }
        )
    def create_member(self, social_account,nickname, introduce, favorite_genre):
        data = {
            "email": social_account.email,  # social_account에서 이메일 가져오기
            "nickname": nickname,
            "introduce": introduce,
            "favorite_genre": favorite_genre,
        }
        serializer = MemberSerializer(data=data)
        if serializer.is_valid():
            return serializer.save()
        raise serializers.ValidationError(serializer.errors)

class Login(APIView):
    def get(self,request):
        social_account = request.session.get("social_account")
        member = User.objects.filter(email=social_account["email"]).first()
        member_dict = model_to_dict(member)
        login(request, member)
        refresh = RefreshToken.for_user(member)
        return Response(
            {
                "message": "Successfully logined",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": member_dict,
            }
        )
class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"msg": "Invalid Token"}, status=400)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"msg": "Successfully Logout"}, status=200)
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
            return Response({"errors":serializer.errors}, status=400)
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
