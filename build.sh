#!/usr/bin/env bash
# Render.com build script
# Poetry installs Python deps into .venv before this script runs.
set -o errexit

# Use Python from Poetry's venv
PYTHON=".venv/bin/python"

# Build Tailwind CSS
npm install
npm run build

# Collect static files
$PYTHON manage.py collectstatic --noinput --settings=config.settings.render

# Copy media files into staticfiles/media/ AFTER collectstatic.
mkdir -p staticfiles/media
cp -r media/. staticfiles/media/

# Run database migrations
$PYTHON manage.py migrate --settings=config.settings.render
