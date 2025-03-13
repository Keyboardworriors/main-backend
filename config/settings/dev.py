import os

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]  # 개발 환경에서는 어디서든 접속 가능

INSTALLED_APPS.append("debug_toolbar")  # 개발 도구 추가

MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = ["127.0.0.1"]

# 개발용 SQLite 또는 PostgreSQL
DATABASES["default"].update(
    {
        "NAME": os.getenv("DB_NAME", "dev_db"),
        "USER": os.getenv("DB_USER", "dev_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "dev_password"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
)
