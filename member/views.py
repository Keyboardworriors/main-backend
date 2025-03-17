import requests
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import SocialAccount
from member.serializer import SocialAccountSerializer, MemberSerializer, \
    ProfileSerializer

User = get_user_model()

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

    def get(self,request,member_id):
        social_account = get_object_or_404(SocialAccount, member=member_id )
        serializer = SocialAccountSerializer(social_account)
        return Response(serializer.data, status=200)

    def patch(self, request, member_id):
        member = get_object_or_404(User,member_id=member_id)
        serializer = MemberSerializer(member, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.validated_data, status=200)

    def delete(self, request, member_id):
        member = get_object_or_404(User, member_id=member_id)
        member.delete()
        return Response({"message":"Successfully deleted"}, status=200)

class MemberProfileView(APIView):
    def get(self,request, member_id):
        member = get_object_or_404(SocialAccount, member=member_id)
        serializer = ProfileSerializer(member)
        return Response(serializer.data, status=200)


