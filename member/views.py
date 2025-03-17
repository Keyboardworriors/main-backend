import requests
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import Member, SocialAccount


class OAuthLogin(APIView):
    def post(self, request):
        provider = request.data.get("provider")  # "kakao" 또는 "naver"
        access_token = request.data.get("access_token")

        if provider not in ["kakao", "naver"]:
            return Response({"error": "Invalid provider"}, status=400)

        user_info = self.get_user_info(provider, access_token)
        if not user_info:
            return Response({"error": "Invalid token"}, status=400)

        email = user_info["email"]
        nickname = user_info.get("nickname", "")
        profile_image = user_info.get("profile_image", "")

        # 🔹 provider_user_id를 기준으로 소셜 계정 조회 or 생성
        social_account, created = SocialAccount.objects.get_or_create(
            provider=provider,
            provider_user_id=user_info["id"],  # ✅ 중복 방지
            defaults={"email": email, "profile_image": profile_image},
        )

        # 🔹 Member 생성 or 연결
        if not social_account.member:
            member, _ = Member.objects.get_or_create(
                email=email, defaults={"nickname": nickname}
            )
            social_account.member = member
            social_account.save()
        else:
            member = social_account.member

        # JWT 발급
        refresh = RefreshToken.for_user(member)

        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

    def get_user_info(self, provider, access_token):
        """
        OAuth 제공자로부터 사용자 정보 조회
        """
        headers = {"Authorization": f"Bearer {access_token}"}

        if provider == "kakao":
            url = "https://kapi.kakao.com/v2/user/me"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return None

            data = response.json()
            return {
                "id": str(data["id"]),
                "email": data["kakao_account"].get("email"),
                "nickname": data["kakao_account"]
                .get("profile", {})
                .get("nickname", ""),
                "profile_image": data["kakao_account"]
                .get("profile", {})
                .get("thumbnail_image_url", ""),
            }

        elif provider == "naver":
            url = "https://openapi.naver.com/v1/nid/me"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return None

            data = response.json().get("response", {})
            return {
                "id": data.get("id"),
                "email": data.get("email"),
                "nickname": data.get("nickname", ""),
                "profile_image": data.get("profile_image", ""),
            }

        return None


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")  # ✅ 필드명 수정
            if not refresh_token:
                return Response({"msg": "Invalid Token"}, status=400)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"msg": "Successfully Logout"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class MemberView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        member = get_object_or_404(Member, email=request.user.email)
        return Response(
            {
                "email": member.email,
                "nickname": member.nickname,
                "introduce": member.introduce,
                "favorite_genre": member.favorite_genre,
                "profile_image": (
                    member.social_accounts.first().profile_image
                    if member.social_accounts.exists()
                    else None
                ),
            },
            status=200,
        )
