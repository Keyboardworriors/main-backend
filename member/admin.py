from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MemberInfo, SocialAccount


class SocialAccountAdmin(UserAdmin):
    model = SocialAccount

    # 기본 필드 설정
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("provider", "provider_user_id", "profile_image")},
        ),
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
                "fields": (
                    "email",
                    "provider",
                    "provider_user_id",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = (
        "email",
        "provider",
        "provider_user_id",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "provider")
    ordering = ("email",)


class MemberInfoAdmin(admin.ModelAdmin):
    model = MemberInfo

    # 필드 설정
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "nickname",
                    "introduce",
                    "favorite_genre",
                    "social_account",
                )
            },
        ),
    )
    list_display = ("nickname", "introduce", "favorite_genre", "social_account")
    list_filter = ("nickname",)
    search_fields = ("nickname", "favorite_genre")
    ordering = ("nickname",)


# 모델 등록
admin.site.register(SocialAccount, SocialAccountAdmin)
admin.site.register(MemberInfo, MemberInfoAdmin)
