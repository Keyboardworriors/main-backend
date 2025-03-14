from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Member, SocialAccount


class MemberAdmin(UserAdmin):
    model = Member
    # 기본 필드 설정
    fieldsets = (
        (None, {"fields": ("email", "nickname", "password")}),
        ("Personal info", {"fields": ("introduce", "favorite_genre")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nickname", "password1", "password2"),
            },
        ),
    )
    list_display = (
        "email",
        "nickname",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "nickname")
    ordering = ("email",)


class SocialAccountAdmin(admin.ModelAdmin):
    model = SocialAccount
    # 필드 설정
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "member",
                    "provider",
                    "provider_user_id",
                    "email",
                    "profile_image",
                )
            },
        ),
        ("Dates", {"fields": ("created_at",)}),
    )
    list_display = ("email", "provider", "provider_user_id", "created_at")
    list_filter = ("provider",)
    search_fields = ("email", "provider", "provider_user_id")
    ordering = ("created_at",)


# 모델 등록
admin.site.register(Member, MemberAdmin)
admin.site.register(SocialAccount, SocialAccountAdmin)
