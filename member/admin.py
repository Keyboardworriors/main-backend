from django.contrib import admin

from .models import MemberInfo, SocialAccount


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = (
        "social_account_id",
        "provider",
        "provider_user_id",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    search_fields = ("email", "provider_user_id")
    list_filter = ("provider", "is_active", "is_staff", "is_superuser")
    readonly_fields = ("social_account_id", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(MemberInfo)
class MemberInfoAdmin(admin.ModelAdmin):
    list_display = (
        "member_info_id",
        "nickname",
        "social_account",
        "introduce",
        "created_at",
    )
    search_fields = ("nickname", "social_account__email")
    list_filter = ("favorite_genre",)
    readonly_fields = ("member_info_id", "created_at", "updated_at")
    ordering = ("-created_at",)
