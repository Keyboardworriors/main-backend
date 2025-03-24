FROM python:3.13-slim-buster

WORKDIR /app

# Poetry 설치
RUN pip install poetry

# Poetry 관련 파일 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치 (프로덕션 환경)
RUN poetry install --no-root --without dev

# 프로젝트 코드 복사
COPY . .

# 환경 변수 설정 (필요에 따라)
ENV DJANGO_SETTINGS_MODULE=main-backend.settings
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행 명령어
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "main-backend.wsgi:application"]