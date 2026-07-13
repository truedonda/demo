"""
Render.com production settings.
Inherits from base.py (NOT production.py) to avoid DB_NAME/DB_USER/DB_PASSWORD
requirements — Render provides DATABASE_URL instead.

Security settings from production.py are replicated here explicitly.
"""
import os
import dj_database_url
from .base import *

# ── Core ──────────────────────────────────────────────────────────────────────
DEBUG = False

# Secret key — must be set via Render environment variable
_secret = os.environ.get('DJANGO_SECRET_KEY', '')
if not _secret:
    raise Exception('DJANGO_SECRET_KEY environment variable is not set.')
SECRET_KEY = _secret

# Allowed hosts — set via Render environment variable
_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(',') if h.strip()] if _hosts else []

# ── Security ──────────────────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── Database — DATABASE_URL from Render ───────────────────────────────────────
_db_url = os.environ.get('DATABASE_URL', '')
if not _db_url:
    raise Exception('DATABASE_URL environment variable is not set.')
DATABASES = {
    'default': dj_database_url.parse(
        _db_url,
        conn_max_age=60,
        engine='django.db.backends.postgresql',
        ssl_require=True,
    )
}
# psycopg3 compatibility: ensure ENGINE uses psycopg3 if available
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'

# ── Cache — Redis from Render ─────────────────────────────────────────────────
_redis_url = os.environ.get('REDIS_URL', '')
if _redis_url:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': _redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': False,
            },
            'KEY_PREFIX': 'cozyshop',
            'TIMEOUT': 60 * 15,
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# ── Static files — WhiteNoise ─────────────────────────────────────────────────
_security_idx = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
MIDDLEWARE.insert(_security_idx + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Media files — Cloudinary ─────────────────────────────────────────────────
INSTALLED_APPS = INSTALLED_APPS + ['cloudinary_storage', 'cloudinary']
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'wktsuy46'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '884289483164339'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'LY-bvwsOOlQhyLvDve475MwfWwQ'),
}

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': False,
        },
    },
}
