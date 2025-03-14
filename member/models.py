import uuid
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields.array import ArrayField
from django.db import models


class MemberManager(BaseUserManager):
    def create_user(self, email, nickname, password=None, **extra_fields):
        """
        이메일을 사용한 일반 사용자 생성 메서드
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        슈퍼유저 생성 메서드
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
# 내부 회원 정보 관리 테이블
class Member(AbstractBaseUser):
    member_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    nickname = models.CharField(max_length=20, unique=True, blank=False)
    introduce = models.CharField(max_length=50, blank=True )
    favorite_genre = ArrayField(models.CharField(max_length=10), blank=True, default=list)
    is_staff = models.BooleanField(default=False)
    is_superuser= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = MemberManager()
    class Meta:
        verbose_name="멤버"
        verbose_name_plural="멤버 목록"

    def __str__(self):
        return self.nickname
    # admin page 용
    @classmethod
    def get_by_natural_key(cls, email):
        return cls.objects.get(email=email)

# 소셜 계정 테이블
class SocialAccount(models.Model):
    social_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)
    provider_user_id = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    profile_image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name= '소셜 계정'
        verbose_name_plural= '소셜 계정 목록'

    def __str__(self):
        return self.email