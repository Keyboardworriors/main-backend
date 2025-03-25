import copy

import requests
from django.contrib.auth import get_user_model, login
from django.forms.models import model_to_dict
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
    @swagger_auto_schema(
        responses={status.HTTP_200_OK: openapi.Response("성공")}
    )
    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="소셜 계정 이메일"
                ),
                "nickname": openapi.Schema(
                    type=openapi.TYPE_STRING, description="사용자 닉네임"
                ),
                "introduce": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="자기소개",
                    nullable=True,
                ),
                "favorite_genre": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description="선호 장르 목록",
                    nullable=True,
                ),
            },
            required=["email", "nickname"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="로그인 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "access_token": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                        "refresh_token": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "email": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "profile_image": openapi.Schema(
                                    type=openapi.TYPE_STRING, nullable=True
                                ),
                                "nickname": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "introduce": openapi.Schema(
                                    type=openapi.TYPE_STRING, nullable=True
                                ),
                                "favorite_genre": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    nullable=True,
                                ),
                            },
                        ),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="유효하지 않은 데이터",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    },
                ),
            ),
        },
    )
    def post(self, request):
        email = request.data.get("email")
        nickname = request.data.get("nickname")
        introduce = request.data.get("introduce")
        favorite_genre = request.data.get("favorite_genre")

        if not email or not nickname:
            return Response(
                {"error": "Email and nickname are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        social_account = SocialAccount.objects.filter(email=email).first()
        if not social_account:
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"email": openapi.Schema(type=openapi.TYPE_STRING)},
            required=["email"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="로그인 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "access_token": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                        "refresh_token": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "email": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "profile_image": openapi.Schema(
                                    type=openapi.TYPE_STRING, nullable=True
                                ),
                                "nickname": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                            },
                        ),
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="유효하지 않은 이메일",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    },
                ),
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="회원 정보 등록이 필요합니다.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    },
                ),
            ),
        },
    )
    def post(self, request):
        email = request.data.get("email")
        if email is None:
            return Response(
                {"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST
            )
        member_info = MemberInfo.objects.filter(
            social_account__email=email
        ).first()

        if not member_info or not member_info.social_account.is_active:
            return Response(
                {"error": "Member information registration is required"},
                status=status.HTTP_404_NOT_FOUND,
            )

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
            status=status.HTTP_200_OK,
        )


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh_token": openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=["refresh_token"],
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="성공적으로 로그아웃되었습니다.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="유효하지 않은 토큰",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    },
                ),
            ),
        },
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"message": "Invalid token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class MemberMypageView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="회원 정보",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "nickname": openapi.Schema(type=openapi.TYPE_STRING),
                        "introduce": openapi.Schema(
                            type=openapi.TYPE_STRING, nullable=True
                        ),
                        "favorite_genre": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                        ),
                        "social_account": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),  # 필요에 따라 더 구체적인 스키마 정의
                    },
                ),
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="회원 정보를 찾을 수 없습니다.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING)
                    },
                ),
            ),
        }
    )
    def get(self, request):
        member_info = MemberInfo.objects.filter(
            social_account=request.user
        ).first()
        if not member_info:
            return Response(
                {"error": "Member information not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MemberInfoSerializer(member_info)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nickname": openapi.Schema(
                    type=openapi.TYPE_STRING, nullable=True
                ),
                "introduce": openapi.Schema(
                    type=openapi.TYPE_STRING, nullable=True
                ),
                "favorite_genre": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    nullable=True,
                ),
                "social_account": openapi.Schema(
                    type=openapi.TYPE_STRING, nullable=True
                ),  # 필요에 따라 더 구체적인 스키마 정의
            },
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="업데이트된 회원 정보",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "nickname": openapi.Schema(type=openapi.TYPE_STRING),
                        "introduce": openapi.Schema(
                            type=openapi.TYPE_STRING, nullable=True
                        ),
                        "favorite_genre": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                        ),
                        "social_account": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),  # 필요에 따라 더 구체적인 스키마 정의
                    },
                ),
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="유효성 검사 오류",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "errors": openapi.Schema(type=openapi.TYPE_OBJECT)
                    },
                ),
            ),
        },
    )
    def patch(self, request):
        social_account = request.user
        member_info = MemberInfo.objects.filter(
            social_account=social_account
        ).first()
        serializer = MemberInfoSerializer(
            member_info, data=request.data, partial=True
        )

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="성공적으로 삭제되었습니다.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING)
                    },
                ),
            )
        }
    )
    def delete(self, request):
        social_account = request.user

        social_account.delete()
        return Response(
            {"message": "Successfully deleted"}, status=status.HTTP_200_OK
        )


class MemberProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="회원 프로필 정보", schema=ProfileSerializer
            )
        }
    )
    def get(self, request):
        member_info = MemberInfo.objects.filter(
            social_account=request.user
        ).first()
        serializer = ProfileSerializer(member_info)
        return Response(serializer.data, status=status.HTTP_200_OK)
