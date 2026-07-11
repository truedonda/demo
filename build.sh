#!/usr/bin/env bash
# Render.com build script
# Poetry installs Python dependencies automatically before this script runs.
# We only need to handle npm, collectstatic, media copy, and migrate.
set -o errexit

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
