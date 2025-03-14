import os

env = os.getenv("DJANGO_ENV", "dev")  # 기본값은 dev
if env == "prod":
    from .prod import *
else:
    from .dev import *
SECRET_KEY=secrets.get("SECRET_KEY")