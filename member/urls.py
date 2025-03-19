from django.urls import path

from member.views import Logout, MemberMypageView, MemberProfileView, Login, \
    MemberRegister

app_name = "member"
urlpatterns = [
    path("register/", MemberRegister.as_view(), name="register"),
    path("login/", Login.as_view(), name="login"),
    path("logout/", Logout.as_view(), name="logout"),
    path("mypage/<uuid:member_id>", MemberMypageView.as_view(), name="mypage"),
    path(
        "profile/<uuid:member_id>", MemberProfileView.as_view(), name="profile"
    ),
]
