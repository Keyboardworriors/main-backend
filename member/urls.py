from django.urls import path

from member.views import Logout, MemberMypageView, MemberProfileView

app_name = "member"
urlpatterns = [
    path("logout/", Logout.as_view(), name="logout"),
    path("mypage/<uuid:member_id>", MemberMypageView.as_view(), name="mypage"),
    path(
        "profile/<uuid:member_id>", MemberProfileView.as_view(), name="profile"
    ),
]
