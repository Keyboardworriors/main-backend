import os

from .base import *

dotenv_path = BASE_DIR / "prod.env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    print(f"파일이 존재하지 않음: {dotenv_path}")
DEBUG = False
ALLOWED_HOSTS = ["www.feelody.site", "feelody.site"]  # 배포 시 실제 도메인

# 보안 강화
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS 설정 (HTTPS 강제)
SECURE_HSTS_SECONDS = 31536000  # 1년 동안 HTTPS 강제
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


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
    "corsheaders",
    # django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

ROOT_URLCONF = "config.urls.prod_urls"
# 로깅 설정
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s [%(levelname)s] %(message)s"},
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "app.log"),
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO",
    },
}
