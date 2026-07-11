#!/usr/bin/env bash
# Render.com build script
set -o errexit

# Install Python dependencies via Poetry
poetry install --no-interaction --no-ansi

# Build Tailwind CSS
npm install
npm run build

# Collect static files
poetry run python manage.py collectstatic --noinput --settings=config.settings.render

# Copy media files into staticfiles/media/ AFTER collectstatic.
mkdir -p staticfiles/media
cp -r media/. staticfiles/media/

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
