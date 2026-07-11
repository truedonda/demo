"""
Local development settings.
Loads environment variables from .env file automatically.
Enables django-debug-toolbar only in DEBUG mode.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from .base import *

# ── Load .env file ────────────────────────────────────────────────────────────
# Resolve .env relative to the project root (3 levels up from this file)
_BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_BASE_DIR / '.env')

# ── Core settings ─────────────────────────────────────────────────────────────
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

# Load ALLOWED_HOSTS from .env (DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1)
_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _hosts_env.split(',') if h.strip()]

# Override SECRET_KEY from .env if provided
_env_secret = os.environ.get('DJANGO_SECRET_KEY', '')
if _env_secret:
    SECRET_KEY = _env_secret

# ── Database (SQLite for local dev) ──────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Cache (local dev) ─────────────────────────────────────────────────────────
# Use Redis if REDIS_URL is set in .env, otherwise fall back to LocMemCache
# so the project starts without Redis installed locally.
_redis_url = os.environ.get('REDIS_URL', '')
if _redis_url:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': _redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True,
            },
            'KEY_PREFIX': 'cozyshop',
            'TIMEOUT': 60 * 15,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'cozyshop-local',
        }
    }

# ── Django Debug Toolbar ──────────────────────────────────────────────────────
# Disabled — uncomment to re-enable during development
# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']
#
#     MIDDLEWARE = [
#         'debug_toolbar.middleware.DebugToolbarMiddleware',
#     ] + MIDDLEWARE
#
#     INTERNAL_IPS = [
#         '127.0.0.1',
#         '::1',
#         'localhost',
#     ]
#
#     DEBUG_TOOLBAR_CONFIG = {
#         'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
#         'DISABLE_PANELS': {
#             'debug_toolbar.panels.history.HistoryPanel',
#             'debug_toolbar.panels.versions.VersionsPanel',
#             'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#             'debug_toolbar.panels.redirects.RedirectsPanel',
#             'debug_toolbar.panels.profiling.ProfilingPanel',
#         },
#         'SHOW_COLLAPSED': True,
#         'SQL_WARNING_THRESHOLD': 100,
#     }
#
#     DEBUG_TOOLBAR_PANELS = [
#         'debug_toolbar.panels.history.HistoryPanel',
#         'debug_toolbar.panels.versions.VersionsPanel',
#         'debug_toolbar.panels.timer.TimerPanel',
#         'debug_toolbar.panels.settings.SettingsPanel',
#         'debug_toolbar.panels.headers.HeadersPanel',
#         'debug_toolbar.panels.request.RequestPanel',
#         'debug_toolbar.panels.sql.SQLPanel',
#         'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#         'debug_toolbar.panels.templates.TemplatesPanel',
#         'debug_toolbar.panels.cache.CachePanel',
#         'debug_toolbar.panels.signals.SignalsPanel',
#         'debug_toolbar.panels.logging.LoggingPanel',
#         'debug_toolbar.panels.redirects.RedirectsPanel',
#         'debug_toolbar.panels.profiling.ProfilingPanel',
#     ]
