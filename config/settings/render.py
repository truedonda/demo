"""
Render.com production settings.
Extends production.py with Render-specific overrides:
  - WhiteNoise for static files AND media files
  - DATABASE_URL env var support via dj-database-url
  - REDIS_URL from Render Redis add-on

Media strategy:
  Product photos are committed to Git in media/.
  build.sh copies media/ → staticfiles/media/ AFTER collectstatic runs,
  so WhiteNoise serves /media/* directly from STATIC_ROOT/media/.
  WHITENOISE_ROOT is not used — instead we rely on the fact that
  WhiteNoise serves everything under STATIC_ROOT at STATIC_URL,
  and we add a separate URL route for /media/ in urls.py via
  django.views.static.serve (DEBUG=False safe via WhiteNoise).

  Simpler approach used here:
  - STATIC_ROOT = staticfiles/
  - build.sh: cp media/ → staticfiles/media/
  - MEDIA_URL = /static/media/   ← WhiteNoise serves this automatically
  - All image URLs in templates will be /static/media/products/...
"""
import os
import dj_database_url
from .production import *

# ── Database — use DATABASE_URL from Render ───────────────────────────────────
_db_url = os.environ.get('DATABASE_URL', '')
if _db_url:
    DATABASES = {
        'default': dj_database_url.parse(
            _db_url,
            conn_max_age=60,
            conn_health_checks=True,
        )
    }

# ── Static files — WhiteNoise serves them directly ───────────────────────────
# Insert WhiteNoise right after SecurityMiddleware
_security_idx = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
MIDDLEWARE.insert(_security_idx + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Media files — served by WhiteNoise under /static/media/ ──────────────────
# build.sh copies media/ → staticfiles/media/ after collectstatic.
# WhiteNoise serves all files under STATIC_ROOT at STATIC_URL (/static/).
# So /static/media/products/foo.jpg works automatically.
# We override MEDIA_URL so Django's ImageField.url returns the correct path.
MEDIA_URL = '/static/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
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
