"""
Management command to download and attach images to knitwear products.
Uses publicly available image URLs from Unsplash (no API key required for direct CDN links).
"""
import os
import urllib.request
import urllib.error
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.catalog.models import Product, ProductImage


# Map product slug -> list of direct image URLs
# Using Unsplash source API (free, no key needed) with specific photo IDs
KNITWEAR_IMAGES = {
    'cropped-crewneck-grey': [
        'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800&q=80',
        'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&q=80',
    ],
    'tank-top-knit': [
        'https://images.unsplash.com/photo-1583744946564-b52ac1c389c8?w=800&q=80',
        'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800&q=80',
    ],
    'boatneck-sweater': [
        'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=80',
        'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=800&q=80',
    ],
    'hybrid-jumper': [
        'https://images.unsplash.com/photo-1548624313-0396c75e4b1a?w=800&q=80',
        'https://images.unsplash.com/photo-1512327536842-5aa37d1ba3e3?w=800&q=80',
    ],
    'oversized-sweater-pink': [
        'https://images.unsplash.com/photo-1608234808654-2a8875faa7fd?w=800&q=80',
        'https://images.unsplash.com/photo-1614251056798-0a63eda2bb25?w=800&q=80',
    ],
    'logo-tank-top-white': [
        'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800&q=80',
        'https://images.unsplash.com/photo-1562157873-818bc0726f68?w=800&q=80',
    ],
    'zip-up-sweater-black': [
        'https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?w=800&q=80',
        'https://images.unsplash.com/photo-1604644401890-0bd678c83788?w=800&q=80',
    ],
    'back-to-front-high-neck-sweater': [
        'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=800&q=80',
        'https://images.unsplash.com/photo-1512327536842-5aa37d1ba3e3?w=800&q=80',
    ],
    'crewneck-sweater-cream': [
        'https://images.unsplash.com/photo-1614251056798-0a63eda2bb25?w=800&q=80',
        'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&q=80',
    ],
    'bb-logo-cropped-crewneck': [
        'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800&q=80',
        'https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?w=800&q=80',
    ],
    'v-neck-sweater-grey': [
        'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=80',
        'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=800&q=80',
    ],
    'bb-logo-cropped-highneck': [
        'https://images.unsplash.com/photo-1604644401890-0bd678c83788?w=800&q=80',
        'https://images.unsplash.com/photo-1548624313-0396c75e4b1a?w=800&q=80',
    ],
    # Pre-existing knitwear products
    'rafaela-knit-sweater': [
        'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&q=80',
        'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=80',
    ],
    'jw-anderson-jumper': [
        'https://images.unsplash.com/photo-1548624313-0396c75e4b1a?w=800&q=80',
        'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=800&q=80',
    ],
}


def download_image(url: str, timeout: int = 15) -> bytes | None:
    """Download image bytes from URL, return None on failure."""
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
        return None


class Command(BaseCommand):
    help = 'Download and attach images to knitwear products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Delete existing images before adding new ones',
        )

    def handle(self, *args, **options):
        replace = options['replace']

        for slug, urls in KNITWEAR_IMAGES.items():
            try:
                product = Product.objects.get(slug=slug)
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Product not found: {slug}'))
                continue

            if replace:
                deleted_count, _ = product.images.all().delete()
                if deleted_count:
                    self.stdout.write(f'  Deleted {deleted_count} existing image(s) for {product.name}')

            existing_count = product.images.count()
            if existing_count > 0 and not replace:
                self.stdout.write(
                    self.style.WARNING(f'  Skipping {product.name} — already has {existing_count} image(s). Use --replace to overwrite.')
                )
                continue

            self.stdout.write(f'Processing: {product.name}')
            order = 0
            for url in urls:
                self.stdout.write(f'  Downloading: {url[:70]}...')
                data = download_image(url)
                if data is None:
                    self.stdout.write(self.style.ERROR(f'    Failed to download image'))
                    continue

                filename = f'{slug}_{order}.jpg'
                product_image = ProductImage(product=product, order=order)
                product_image.image.save(filename, ContentFile(data), save=True)
                order += 1
                self.stdout.write(self.style.SUCCESS(f'    Saved as products/{filename}'))

            if order == 0:
                self.stdout.write(self.style.ERROR(f'  No images saved for {product.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'  Done: {order} image(s) attached to {product.name}'))

        self.stdout.write(self.style.SUCCESS('\nAll knitwear images processed.'))
