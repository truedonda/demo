#!/usr/bin/env bash
# Render.com build script
set -o errexit

# Render uses Poetry by default and creates a .venv.
# We install via pip into that same venv so packages are available at runtime.
pip install -r requirements.txt

# Build Tailwind CSS
npm install
npm run build

# Collect static files
python manage.py collectstatic --noinput --settings=config.settings.render

# Copy media files into staticfiles/media/ AFTER collectstatic.
mkdir -p staticfiles/media
cp -r media/. staticfiles/media/

# Run database migrations
python manage.py migrate --settings=config.settings.render
