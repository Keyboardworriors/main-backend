import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = ["yourdomain.com"]  # 배포 시 실제 도메인

# 보안 강화
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True  # HTTPS 강제 적용
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# PostgreSQL 배포용 설정
DATABASES["default"].update(
    {
        "NAME": os.getenv("DB_NAME", "prod_db"),
        "USER": os.getenv("DB_USER", "prod_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "prod_password"),
        "HOST": os.getenv("DB_HOST", "prod_db_host"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
)


INSTALLED_APPS = [
    # own apps
    "member",
    "diary",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

ROOT_URLCONF = "config.urls.prod_urls"
