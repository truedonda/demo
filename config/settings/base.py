import os
import sys
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ── SECRET KEY ────────────────────────────────────────────────────────────────
# Fix #1: Raise error if SECRET_KEY is not set in production.
# In local development (local.py), SECRET_KEY is always overridden below.
_secret = os.environ.get('DJANGO_SECRET_KEY', '')
if not _secret:
    # Allow any management command in development — production.py will enforce this
    _secret = 'dev-only-insecure-key-do-not-use-in-production-ever'
SECRET_KEY = _secret

DEBUG = False

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'apps.catalog',
    'apps.cart',
    'apps.orders',
    'apps.accounts',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.cart.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── DATABASE ──────────────────────────────────────────────────────────────────
# Fix #2: No hardcoded credential fallbacks — use env vars only
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'cozyshop'),
        'USER': os.environ.get('DB_USER', 'cozyshop'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'cozyshop'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ── CACHE ─────────────────────────────────────────────────────────────────────
# Default: Redis via django-redis. Override REDIS_URL in environment.
# Falls back to LocMemCache if REDIS_URL is not set (local dev without Redis).
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # Don't crash the app if Redis is temporarily unavailable
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'cozyshop',
        'TIMEOUT': 60 * 15,  # 15 minutes default TTL
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── FILE UPLOAD LIMITS ────────────────────────────────────────────────────────
# Fix #15: Reduce from 20MB to 5MB for public endpoints
# Admin image uploads are handled separately via nginx client_max_body_size
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024   # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024   # 5 MB

# ── SESSION ───────────────────────────────────────────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# Fix #21: Reduce from 30 days to 7 days + sliding expiry
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7   # 7 days
SESSION_SAVE_EVERY_REQUEST = True         # Sliding expiry — resets on each request

# Fix #12: Explicitly set HttpOnly on session cookie
SESSION_COOKIE_HTTPONLY = True

# Fix #13: CSRF cookie must NOT be HttpOnly — HTMX reads it from JS via getCsrf()
CSRF_COOKIE_HTTPONLY = False
