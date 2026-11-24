"""Local development settings: debug on, permissive hosts, admin endpoints enabled."""

from config.settings.base import *
from config.settings.base import env

ENVIRONMENT = "development"
DEBUG = True
SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-only-insecure-secret-key-change-me")
JWT_KEY = env("JWT_KEY", default="dev-only-insecure-jwt-key-change-me-0123456789")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "[::1]"])
ENABLE_DB_ADMIN_ENDPOINTS = True
