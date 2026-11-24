"""
Production settings. Fails fast at startup when a required secret is missing,
rather than running with an insecure fallback.
"""

from django.core.exceptions import ImproperlyConfigured

from config.settings.base import *
from config.settings.base import ALLOWED_HOSTS, JWT_KEY, SECRET_KEY, env

ENVIRONMENT = "production"
DEBUG = False

if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set and at least 50 characters long.")
if len(JWT_KEY) < 32:
    raise ImproperlyConfigured("JWT_KEY must be set and at least 32 characters long.")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must list the public hostnames.")

# Serve behind TLS termination; the proxy must set X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# Preloading is a commitment that is hard to reverse; enable it deliberately.
SECURE_HSTS_PRELOAD = env.bool("DJANGO_HSTS_PRELOAD", default=False)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
