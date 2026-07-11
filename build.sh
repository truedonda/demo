#!/usr/bin/env bash
# Render.com build script
set -o errexit

# Install Python dependencies via Poetry into .venv
poetry install --no-interaction --no-ansi

# Build Tailwind CSS
npm install
npm run build

# Collect static files (use Poetry's venv python)
poetry run python manage.py collectstatic --noinput --settings=config.settings.render

# Copy media files into staticfiles/media/ AFTER collectstatic.
mkdir -p staticfiles/media
cp -r media/. staticfiles/media/

# Run database migrations
poetry run python manage.py migrate --settings=config.settings.render
