"""
Management command: upload all local media files to Cloudinary.
Run once after switching to Cloudinary storage to migrate existing images.
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Upload all local media/products/ files to Cloudinary'

    def handle(self, *args, **kwargs):
        try:
            import cloudinary.uploader
        except ImportError:
            self.stderr.write('cloudinary not installed')
            return

        media_root = Path(settings.BASE_DIR) / 'media'
        if not media_root.exists():
            self.stderr.write(f'media/ not found at {media_root}')
            return

        uploaded = 0
        for img_path in media_root.rglob('*.jpg'):
            # public_id = relative path without extension, e.g. "products/foo_0"
            rel = img_path.relative_to(media_root)
            public_id = str(rel.with_suffix('')).replace('\\', '/')
            try:
                cloudinary.uploader.upload(
                    str(img_path),
                    public_id=public_id,
                    overwrite=False,
                    resource_type='image',
                )
                self.stdout.write(f'  uploaded: {public_id}')
                uploaded += 1
            except Exception as e:
                self.stderr.write(f'  skip {public_id}: {e}')

        self.stdout.write(self.style.SUCCESS(f'Done: {uploaded} files uploaded to Cloudinary'))
