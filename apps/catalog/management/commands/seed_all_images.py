"""
Management command to download and attach Unsplash images to all products
that currently have no images.
"""
import urllib.request
import urllib.error
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.catalog.models import Product, ProductImage


# Map product slug -> list of direct Unsplash image URLs (2 per product)
PRODUCT_IMAGES = {
    # ── WOMAN · Outerwear ──────────────────────────────────────────────────
    'mavis-oversized-trench': [
        'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800&q=80',
        'https://images.unsplash.com/photo-1548624313-0396c75e4b1a?w=800&q=80',
    ],
    'naica-leather-jacket': [
        'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80',
        'https://images.unsplash.com/photo-1521223890158-f9f7c3d5d504?w=800&q=80',
    ],
    'arlise-trench-coat': [
        'https://images.unsplash.com/photo-1544022613-e87ca75a784a?w=800&q=80',
        'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800&q=80',
    ],
    'peoria-suede-blazer': [
        'https://images.unsplash.com/photo-1594938298603-c8148c4b4f7b?w=800&q=80',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',
    ],
    'iva-blazer': [
        'https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=800&q=80',
        'https://images.unsplash.com/photo-1594938298603-c8148c4b4f7b?w=800&q=80',
    ],
    'shay-trench-coat': [
        'https://images.unsplash.com/photo-1548624313-0396c75e4b1a?w=800&q=80',
        'https://images.unsplash.com/photo-1544022613-e87ca75a784a?w=800&q=80',
    ],
    'lena-wool-coat': [
        'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800&q=80',
        'https://images.unsplash.com/photo-1520975954732-35dd22299614?w=800&q=80',
    ],
    'mira-puffer-jacket': [
        'https://images.unsplash.com/photo-1608234808654-2a8875faa7fd?w=800&q=80',
        'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80',
    ],

    # ── WOMAN · Knitwear (extra, not yet seeded) ───────────────────────────
    'aria-mohair-cardigan': [
        'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&q=80',
        'https://images.unsplash.com/photo-1614251056798-0a63eda2bb25?w=800&q=80',
    ],
    'nova-ribbed-turtleneck': [
        'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=800&q=80',
        'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800&q=80',
    ],

    # ── WOMAN · Tops ───────────────────────────────────────────────────────
    'prilly-oversized-shirt': [
        'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800&q=80',
        'https://images.unsplash.com/photo-1562157873-818bc0726f68?w=800&q=80',
    ],
    'beaufille-baes-crop-top': [
        'https://images.unsplash.com/photo-1583744946564-b52ac1c389c8?w=800&q=80',
        'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800&q=80',
    ],
    'silk-cami-top': [
        'https://images.unsplash.com/photo-1594938298603-c8148c4b4f7b?w=800&q=80',
        'https://images.unsplash.com/photo-1583744946564-b52ac1c389c8?w=800&q=80',
    ],
    'lace-corset-top': [
        'https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=800&q=80',
        'https://images.unsplash.com/photo-1594938298603-c8148c4b4f7b?w=800&q=80',
    ],
    'wrap-blouse-woman': [
        'https://images.unsplash.com/photo-1562157873-818bc0726f68?w=800&q=80',
        'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=800&q=80',
    ],

    # ── WOMAN · Bottoms ────────────────────────────────────────────────────
    'wide-leg-trousers-woman': [
        'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80',
        'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=80',
    ],
    'mini-skirt-black': [
        'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800&q=80',
        'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80',
    ],
    'midi-slit-skirt': [
        'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=80',
        'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800&q=80',
    ],
    'tailored-shorts-woman': [
        'https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=800&q=80',
        'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80',
    ],

    # ── WOMAN · Dresses ────────────────────────────────────────────────────
    'slip-dress-satin': [
        'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=800&q=80',
        'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800&q=80',
    ],
    'knit-midi-dress': [
        'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800&q=80',
        'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=800&q=80',
    ],
    'wrap-midi-dress': [
        'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&q=80',
        'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800&q=80',
    ],
    'maxi-evening-dress': [
        'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=800&q=80',
        'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&q=80',
    ],

    # ── WOMAN · Jumpsuits ──────────────────────────────────────────────────
    'tailored-jumpsuit-woman': [
        'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80',
        'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=800&q=80',
    ],
    'linen-jumpsuit-woman': [
        'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800&q=80',
        'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80',
    ],

    # ── WOMAN · Loungewear ─────────────────────────────────────────────────
    'cashmere-lounge-set-woman': [
        'https://images.unsplash.com/photo-1614251056798-0a63eda2bb25?w=800&q=80',
        'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&q=80',
    ],
    'velvet-robe-woman': [
        'https://images.unsplash.com/photo-1608234808654-2a8875faa7fd?w=800&q=80',
        'https://images.unsplash.com/photo-1614251056798-0a63eda2bb25?w=800&q=80',
    ],

    # ── MAN · Outerwear ────────────────────────────────────────────────────
    'arbor-leather-jacket': [
        'https://images.unsplash.com/photo-1521223890158-f9f7c3d5d504?w=800&q=80',
        'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80',
    ],
    'pelso-barn-jacket': [
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',
        'https://images.unsplash.com/photo-1521223890158-f9f7c3d5d504?w=800&q=80',
    ],
    'rex-bomber-jacket': [
        'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&q=80',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',
    ],
    'cole-overcoat': [
        'https://images.unsplash.com/photo-1520975954732-35dd22299614?w=800&q=80',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',
    ],
    'denim-trucker-jacket': [
        'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80',
        'https://images.unsplash.com/photo-1521223890158-f9f7c3d5d504?w=800&q=80',
    ],
    'field-jacket-man': [
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',
        'https://images.unsplash.com/photo-1520975954732-35dd22299614?w=800&q=80',
    ],

    # ── MAN · Knitwear (extra) ─────────────────────────────────────────────
    'cable-knit-sweater-man': [
        'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=80',
        'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=800&q=80',
    ],
    'half-zip-pullover-man': [
        'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=800&q=80',
        'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&q=80',
    ],

    # ── MAN · Tops ─────────────────────────────────────────────────────────
    'rotate-oversized-t-shirt': [
        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&q=80',
        'https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=800&q=80',
    ],
    'oxford-button-down-man': [
        'https://images.unsplash.com/photo-1603252109303-2751441dd157?w=800&q=80',
        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&q=80',
    ],
    'linen-shirt-man': [
        'https://images.unsplash.com/photo-1503341504253-dff4815485f1?w=800&q=80',
        'https://images.unsplash.com/photo-1603252109303-2751441dd157?w=800&q=80',
    ],
    'graphic-tee-man': [
        'https://images.unsplash.com/photo-1529374255404-311a2a4f1fd9?w=800&q=80',
        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&q=80',
    ],
    'polo-shirt-man': [
        'https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=800&q=80',
        'https://images.unsplash.com/photo-1603252109303-2751441dd157?w=800&q=80',
    ],

    # ── MAN · Bottoms ──────────────────────────────────────────────────────
    'slim-chinos-man': [
        'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=80',
        'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80',
    ],
    'wide-leg-trousers-man': [
        'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80',
        'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=80',
    ],
    'cargo-pants-man': [
        'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80',
        'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&q=80',
    ],
    'tailored-shorts-man': [
        'https://images.unsplash.com/photo-1591369822096-ffd140ec948f?w=800&q=80',
        'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&q=80',
    ],

    # ── MAN · Loungewear ───────────────────────────────────────────────────
    'terry-tracksuit-man': [
        'https://images.unsplash.com/photo-1556906781-9a412961a28c?w=800&q=80',
        'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&q=80',
    ],
    'fleece-hoodie-man': [
        'https://images.unsplash.com/photo-1556906781-9a412961a28c?w=800&q=80',
        'https://images.unsplash.com/photo-1529374255404-311a2a4f1fd9?w=800&q=80',
    ],
    'sweatpants-man': [
        'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80',
        'https://images.unsplash.com/photo-1556906781-9a412961a28c?w=800&q=80',
    ],

    # ── MAN · Jumpsuits ────────────────────────────────────────────────────
    'utility-jumpsuit-man': [
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',
        'https://images.unsplash.com/photo-1542272604-787c3835535d?w=800&q=80',
    ],
}


def download_image(url: str, timeout: int = 20) -> bytes | None:
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
    except Exception:
        return None


class Command(BaseCommand):
    help = 'Download and attach Unsplash images to all products without images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Delete existing images before adding new ones',
        )
        parser.add_argument(
            '--slug',
            type=str,
            default=None,
            help='Only process a specific product slug',
        )

    def handle(self, *args, **options):
        replace = options['replace']
        only_slug = options['slug']

        items = PRODUCT_IMAGES.items()
        if only_slug:
            items = [(only_slug, PRODUCT_IMAGES[only_slug])] if only_slug in PRODUCT_IMAGES else []

        attached_total = 0
        skipped_total = 0
        failed_total = 0

        for slug, urls in items:
            try:
                product = Product.objects.get(slug=slug)
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Product not found: {slug}'))
                continue

            if replace:
                deleted, _ = product.images.all().delete()
                if deleted:
                    self.stdout.write(f'  Deleted {deleted} existing image(s) for "{product.name}"')

            existing_count = product.images.count()
            if existing_count > 0 and not replace:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Skipping "{product.name}" — already has {existing_count} image(s).'
                    )
                )
                skipped_total += 1
                continue

            self.stdout.write(f'Processing: {product.name}')
            order = 0
            for url in urls:
                self.stdout.write(f'  Downloading: {url[:70]}...')
                data = download_image(url)
                if data is None:
                    self.stdout.write(self.style.ERROR(f'    Failed to download'))
                    failed_total += 1
                    continue

                filename = f'{slug}_{order}.jpg'
                pi = ProductImage(product=product, order=order)
                pi.image.save(filename, ContentFile(data), save=True)
                order += 1
                attached_total += 1
                self.stdout.write(self.style.SUCCESS(f'    Saved: products/{filename}'))

            if order == 0:
                self.stdout.write(self.style.ERROR(f'  No images saved for "{product.name}"'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done. Attached {attached_total} image(s). '
            f'Skipped {skipped_total} product(s). '
            f'Failed downloads: {failed_total}.'
        ))
