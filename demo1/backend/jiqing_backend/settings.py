import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEV_SECRET_KEY = "dev-only-change-before-deploy"
SECRET_KEY = os.environ.get("JIQING_SECRET_KEY", DEV_SECRET_KEY)
DEBUG = os.environ.get("JIQING_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("JIQING_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]
AGENT_SERVICE_KEY = os.environ.get("JIQING_AGENT_SERVICE_KEY", "")

if not DEBUG and SECRET_KEY == DEV_SECRET_KEY:
    raise RuntimeError("生产环境必须设置独立的 JIQING_SECRET_KEY")
if not DEBUG and len(AGENT_SERVICE_KEY) < 32:
    raise RuntimeError("生产环境的 JIQING_AGENT_SERVICE_KEY 不少于32个字符")
if not DEBUG and not ALLOWED_HOSTS:
    raise RuntimeError("生产环境必须设置 JIQING_ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jiqing_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "jiqing_backend.wsgi.application"

SQLITE_PATH = os.environ.get("JIQING_SQLITE_PATH", str(BASE_DIR / "db.sqlite3"))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": SQLITE_PATH,
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AGENT_CONFIRMATION_MAX_AGE_SECONDS = int(
    os.environ.get("JIQING_AGENT_CONFIRMATION_MAX_AGE_SECONDS", "300")
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
