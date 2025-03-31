import copy
import logging

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
logger = logging.getLogger(__name__)


class CreateMemberInfo(APIView):
    def get(self, request):
        logger.info("GET request received for CreateMemberInfo")
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        logger.info("POST request received for CreateMemberInfo")
        email = request.data.get("email")
        nickname = request.data.get("nickname")
        introduce = request.data.get("introduce")
        favorite_genre = request.data.get("favorite_genre")

        if not email or not nickname:
            logger.warning("Email and nickname are required")
            return Response(
                {"error": "Email and nickname are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        social_account = SocialAccount.objects.filter(email=email).first()
        if not social_account:
            logger.warning(f"Social account not found for email: {email}")
            return Response(
                {"error": "Social account not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {
            "nickname": nickname,
            "introduce": introduce,
            "favorite_genre": favorite_genre,
            "social_account": social_account.social_account_id,
        }

        serializer = MemberInfoSerializer(data=data)
        if serializer.is_valid():
            social_account.is_active = True
            social_account.save()
            serializer.save()
            logger.info(f"Member info created for email: {email}")

            refresh = RefreshToken.for_user(social_account)
            return Response(
                {
                    "message": "Successfully logged in",
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
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    def post(self, request):
        logger.info("POST request received for Login")
        email = request.data.get("email")
        if email is None:
            logger.warning("Invalid email provided")
            return Response(
                {"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST
            )
        member_info = MemberInfo.objects.filter(
            social_account__email=email
        ).first()

        if not member_info or not member_info.social_account.is_active:
            logger.warning(
                f"Member information registration required for email: {email}"
            )
            return Response(
                {"error": "Member information registration is required"},
                status=status.HTTP_404_NOT_FOUND,
            )

        refresh = RefreshToken.for_user(member_info.social_account)
        social_account_serializer = SocialAccountSerializer(
            member_info.social_account
        )

        logger.info(f"Successful login for email: {email}")
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
            status=status.HTTP_200_OK,
        )


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info("POST request received for Logout")
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                logger.warning("Invalid token provided for logout")
                return Response(
                    {"message": "Invalid token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("User successfully logged out")
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class MemberMypageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info("GET request received for MemberMypageView")
        member_info = MemberInfo.objects.filter(
            social_account=request.user
        ).first()
        if not member_info:
            logger.warning(
                f"Member information not found for user: {request.user}"
            )
            return Response(
                {"error": "Member information not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MemberInfoSerializer(member_info)
        data = {
            "nickname": serializer.data["nickname"],
            "introduce": serializer.data.get("introduce"),
            "favorite_genre": serializer.data.get("favorite_genre"),
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        logger.info("PATCH request received for MemberMypageView")
        social_account = request.user
        member_info = MemberInfo.objects.filter(
            social_account=social_account
        ).first()
        serializer = MemberInfoSerializer(
            member_info, data=request.data, partial=True
        )

        if not serializer.is_valid():
            logger.warning(f"Serializer validation errors: {serializer.errors}")
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        logger.info(f"Member info updated for user: {social_account}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        logger.info("DELETE request received for MemberMypageView")
        social_account = request.user

        social_account.delete()
        logger.info(f"User account deleted: {social_account}")
        return Response(
            {"message": "Successfully deleted"}, status=status.HTTP_200_OK
        )


class MemberProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info("GET request received for MemberProfileView")
        member_info = MemberInfo.objects.filter(
            social_account=request.user
        ).first()
        serializer = ProfileSerializer(member_info)
        return Response(serializer.data, status=status.HTTP_200_OK)
