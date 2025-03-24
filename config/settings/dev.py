import os

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]  # 개발 환경에서는 어디서든 접속 가능

# INSTALLED_APPS.append("debug_toolbar")  # 개발 도구 추가

# MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = ["*"]

ROOT_URLCONF = "config.urls.dev_urls"
