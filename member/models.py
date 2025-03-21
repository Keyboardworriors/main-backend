import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.manager import Manager


class SocialAccountManager(BaseUserManager):
    """
    커스텀 유저 모델 관리자
    """

    def create_user(self, email, provider, provider_user_id, profile_image=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            provider=provider,
            provider_user_id=provider_user_id,
            profile_image=profile_image or "",
            **extra_fields,
        )

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, provider, provider_user_id, password=None, **extra_fields):
        """
        슈퍼유저 생성 메서드
        """
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, provider, provider_user_id, password=password, **extra_fields)


# 소셜 계정을 기본 User 모델로 사용
class SocialAccount(AbstractBaseUser, PermissionsMixin):
    social_account_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    provider = models.CharField(max_length=20)
    provider_user_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    profile_image = models.URLField(blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["provider", "provider_user_id"]

    objects = SocialAccountManager()

    class Meta:
        verbose_name = "소셜 계정"
        verbose_name_plural = "소셜 계정 목록"
        unique_together = ("provider", "provider_user_id")

    def __str__(self):
        return f"{self.provider} - {self.email}"


# 유저 추가 정보 테이블
class MemberInfo(models.Model):
    member_info_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    introduce = models.CharField(max_length=50, null=True, blank=True)
    favorite_genre = ArrayField(
        models.CharField(max_length=10), blank=True, default=list, null=True
    )
    nickname = models.CharField(
        max_length=30, unique=True, null=False, blank=False
    )
    social_account = models.OneToOneField(
        SocialAccount, on_delete=models.CASCADE, related_name="member_info"
    )
    objects = Manager()

    class Meta:
        verbose_name = "유저 정보"
        verbose_name_plural = "유저 정보 목록"

    def __str__(self):
        return f"{self.nickname} ({self.social_account.email})"
