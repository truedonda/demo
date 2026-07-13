#!/usr/bin/env bash
# Render.com build script
set -o errexit

# Install Python dependencies via Poetry
poetry install --no-interaction --no-ansi

# Build Tailwind CSS
npm install
npm run build

# Copy media files into static/media/ BEFORE collectstatic
# so they get picked up as static files and served by WhiteNoise at /static/media/
mkdir -p static/media
cp -r media/. static/media/

# Collect static files (includes static/media/ now)
poetry run python manage.py collectstatic --noinput --settings=config.settings.render

# Run database migrations
poetry run python manage.py migrate --settings=config.settings.render

# Create superuser automatically if DJANGO_SUPERUSER_* env vars are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    poetry run python manage.py createsuperuser \
        --noinput \
        --settings=config.settings.render \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" \
        2>/dev/null || echo "Superuser already exists, skipping."
fi
