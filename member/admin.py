from django.contrib import admin

from member.models import Member, SocialAccount


# Register your models here.
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        "member_id",
        "email",
        "nickname",
        "introduce",
        "favorite_genre",
        "created_at",
        "updated_at",
    ]
    search_fields = ["email", "nickname"]


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = [
        "social_account_id",
        "member_id",
        "provider",
        "provider_user_id",
        "email",
        "created_at",
    ]
    search_fields = ["email", "provider"]
