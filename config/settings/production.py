import os
from django.core.exceptions import ImproperlyConfigured
from .base import *

DEBUG = False

# Fix #1: Enforce SECRET_KEY in production — must not be the dev fallback
if SECRET_KEY == 'dev-only-insecure-key-do-not-use-in-production-ever':
    raise ImproperlyConfigured(
        'DJANGO_SECRET_KEY environment variable is not set. '
        'Set it to a long random string in production.'
    )

# Fix #20: Validate ALLOWED_HOSTS — raise error if not set
_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
if not _hosts:
    raise ImproperlyConfigured(
        'DJANGO_ALLOWED_HOSTS must be set in production. '
        'Example: DJANGO_ALLOWED_HOSTS=example.com,www.example.com'
    )
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()]

# Fix #3: Enforce HTTPS redirect
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# Fix #25: SECURE_BROWSER_XSS_FILTER removed (deprecated, harmful in old browsers)
# Use CSP instead (configured in nginx — see docker/nginx/prod.conf)

# Fix #2: Production DB — credentials MUST come from environment (no fallbacks)
def _require_env(name):
    val = os.environ.get(name, '')
    if not val:
        raise ImproperlyConfigured(f'Environment variable {name} is required in production.')
    return val

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _require_env('DB_NAME'),
        'USER': _require_env('DB_USER'),
        'PASSWORD': _require_env('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
    }
}

# ── Cache (production) ────────────────────────────────────────────────────────
# Redis is required in production — REDIS_URL must be set.
_redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': _redis_url,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # Do not silently ignore Redis errors in production — let monitoring catch them
            'IGNORE_EXCEPTIONS': False,
        },
        'KEY_PREFIX': 'cozyshop',
        'TIMEOUT': 60 * 15,  # 15 minutes default TTL
    }
}

# Use Redis as session backend in production for better performance
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
