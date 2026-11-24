"""
Settings shared by every environment.

Environment-specific modules (``development``, ``production``, ``test``) import
from here and override only what differs. Configuration comes exclusively from
environment variables; ``.env.example`` documents each one.
"""

from __future__ import annotations

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

ENVIRONMENT = "base"

DEBUG = False
SECRET_KEY = env("DJANGO_SECRET_KEY", default="")
ALLOWED_HOSTS: list[str] = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# JWT signing key. Kept separate from SECRET_KEY so the two can rotate independently.
JWT_KEY = env("JWT_KEY", default="")

# Origin of the React client. Used for CORS.
CLIENT_URL = env("CLIENT_URL", default="http://localhost:5173")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
# django.contrib.auth and contenttypes are intentionally NOT installed: their
# models use AutoField, which the MongoDB backend does not support. We still use
# AbstractBaseUser and Django's password hashers, which do not require the apps.
INSTALLED_APPS = [
    "corsheaders",
    "rest_framework",
    "core",
    "accounts",
    "resumes",
    "ai",
    "analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # CommonMiddleware validates the Host header against ALLOWED_HOSTS on every request.
    # Without it, ALLOWED_HOSTS is not enforced for API traffic.
    "django.middleware.common.CommonMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.PermissionsPolicyMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database: MongoDB via the official django-mongodb-backend
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": env("MONGODB_URI", default="mongodb://127.0.0.1:27017"),
        "NAME": env("MONGODB_DB", default="resume-builder"),
    }
}
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

# ---------------------------------------------------------------------------
# Authentication and passwords
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Cache: backs DRF throttling and failed-login counters.
# Use Redis in production when running more than one process.
# ---------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="")
if REDIS_URL:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": REDIS_URL}}
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# ---------------------------------------------------------------------------
# Django Rest Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["accounts.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_THROTTLE_CLASSES": ["core.throttling.GlobalIPThrottle"],
    "EXCEPTION_HANDLER": "core.exceptions.api_exception_handler",
    # Set DJANGO_NUM_PROXIES to the number of trusted reverse proxies in front of
    # the app so client IPs are read from X-Forwarded-For correctly.
    "NUM_PROXIES": env.int("DJANGO_NUM_PROXIES", default=0),
    "DEFAULT_PAGINATION_CLASS": None,
    # AnonymousUser lives in django.contrib.auth, which is not installed. None is DRF's
    # documented replacement; IsAuthenticated and our throttles already handle it.
    "UNAUTHENTICATED_USER": None,
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [CLIENT_URL]
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Request and upload limits
# ---------------------------------------------------------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024  # 1 MB JSON bodies, matching the old API
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
RESUME_UPLOAD_MAX_BYTES = 10 * 1024 * 1024

APPEND_SLASH = False  # API routes are slash-less, like the original Express API.

# ---------------------------------------------------------------------------
# Localisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# AI suggestions (any OpenAI-compatible chat completions endpoint)
# ---------------------------------------------------------------------------
OPENAI_KEY = env("OPENAI_KEY", default="")
OPENAI_BASE_URL = env("OPENAI_BASE_URL", default="https://api.openai.com")
OPENAI_MODEL = env("OPENAI_MODEL", default="gemma-3-27b-it")
OPENAI_TIMEOUT_SECONDS = env.float("OPENAI_TIMEOUT_SECONDS", default=20.0)

# CSRF protection is not used: the API authenticates with bearer tokens in the
# Authorization header, which browsers do not attach automatically. Django's
# check framework still reports this, so it is silenced explicitly here.
SILENCED_SYSTEM_CHECKS = ["security.W003"]

# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------
# Allows the analytics setup/seed endpoints. Keep this False outside development.
ENABLE_DB_ADMIN_ENDPOINTS = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
    },
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
