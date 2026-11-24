"""Settings for the automated test suite. Fast password hashing; a fixed key."""

from config.settings.base import *

ENVIRONMENT = "test"
DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"
JWT_KEY = "test-jwt-key-not-for-production-0123456789"
ALLOWED_HOSTS = ["testserver", "localhost"]
ENABLE_DB_ADMIN_ENDPOINTS = True

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
OPENAI_KEY = "test-openai-key"
