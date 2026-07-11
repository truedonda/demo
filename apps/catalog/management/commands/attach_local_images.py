"""
Management command to attach existing local image files from media/products/
to their corresponding Product records in the database.

Image files follow the naming pattern: {product-slug}_{order}.jpg
(e.g. rafaela-knit-sweater_0.jpg, rafaela-knit-sweater_1.jpg)
"""
import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.catalog.models import Product, ProductImage


class Command(BaseCommand):
    help = 'Attach existing local media/products/ images to Product records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Delete existing ProductImage records before attaching',
        )

    def handle(self, *args, **options):
        replace = options['replace']
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')

        if not os.path.isdir(products_dir):
            self.stdout.write(self.style.ERROR(f'Directory not found: {products_dir}'))
            return

        # Collect files that match the clean pattern: {slug}_{order}.jpg
        # Exclude files with extra random suffixes (e.g. slug_0_AbCdEf.jpg)
        pattern = re.compile(r'^(.+)_(\d+)\.jpg$')
        suffix_pattern = re.compile(r'^(.+)_(\d+)_[A-Za-z0-9]+\.jpg$')

        # Build a dict: slug -> sorted list of (order, relative_path)
        slug_images: dict[str, list[tuple[int, str]]] = {}
        for filename in sorted(os.listdir(products_dir)):
            # Skip files with random suffixes
            if suffix_pattern.match(filename):
                continue
            m = pattern.match(filename)
            if not m:
                continue
            slug, order_str = m.group(1), m.group(2)
            rel_path = f'products/{filename}'
            slug_images.setdefault(slug, []).append((int(order_str), rel_path))

        # Sort each slug's images by order
        for slug in slug_images:
            slug_images[slug].sort(key=lambda x: x[0])

        self.stdout.write(f'Found image groups for {len(slug_images)} slug(s) in media/products/')

        attached_total = 0
        skipped_total = 0
        missing_total = 0

        for slug, images in slug_images.items():
            try:
                product = Product.objects.get(slug=slug)
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  No product found for slug: {slug}'))
                missing_total += 1
                continue

            if replace:
                deleted, _ = product.images.all().delete()
                if deleted:
                    self.stdout.write(f'  Deleted {deleted} existing image(s) for "{product.name}"')

            existing_count = product.images.count()
            if existing_count > 0 and not replace:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Skipping "{product.name}" — already has {existing_count} image(s). '
                        f'Use --replace to overwrite.'
                    )
                )
                skipped_total += 1
                continue

            self.stdout.write(f'  Attaching images to "{product.name}" ({slug}):')
            for order, rel_path in images:
                # Check the file actually exists
                abs_path = os.path.join(settings.MEDIA_ROOT, rel_path.replace('/', os.sep))
                if not os.path.isfile(abs_path):
                    self.stdout.write(self.style.ERROR(f'    File missing: {abs_path}'))
                    continue

                # Avoid duplicate entries
                if not replace and product.images.filter(image=rel_path).exists():
                    self.stdout.write(f'    Already linked: {rel_path}')
                    continue

                ProductImage.objects.create(product=product, image=rel_path, order=order)
                self.stdout.write(self.style.SUCCESS(f'    Linked: {rel_path}'))
                attached_total += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done. Attached {attached_total} image record(s). '
            f'Skipped {skipped_total} product(s) with existing images. '
            f'Missing product for {missing_total} slug(s).'
        ))
