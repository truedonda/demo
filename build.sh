#!/usr/bin/env bash
# Render.com build script
# Runs once during each deploy before the web service starts.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Build Tailwind CSS
npm install
npm run build

# Collect static files (CSS, JS, admin, etc.) into staticfiles/
python manage.py collectstatic --noinput --settings=config.settings.render

# Copy media files into staticfiles/media/ AFTER collectstatic.
# WhiteNoise serves everything under STATIC_ROOT (/static/), so
# /static/media/products/foo.jpg will be accessible.
# MEDIA_URL is set to /static/media/ in render.py to match.
mkdir -p staticfiles/media
cp -r media/. staticfiles/media/

# Run database migrations
python manage.py migrate --settings=config.settings.render
