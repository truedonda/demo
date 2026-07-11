import io
import logging
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from PIL import Image

# Fix #18: Prevent image bomb (decompression bomb) attacks
# Limit to 50 megapixels — sufficient for any display, prevents memory exhaustion
Image.MAX_IMAGE_PIXELS = 50_000_000

logger = logging.getLogger(__name__)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        if self.image:
            _compress_image_field(self.image)


class Product(models.Model):
    GENDER_CHOICES = [
        ('woman', 'Woman'),
        ('man', 'Man'),
        ('unisex', 'Unisex'),
    ]

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sizes = models.JSONField(default=list, blank=True)
    unavailable_sizes = models.JSONField(default=list, blank=True, help_text='Sizes that are sold out (will be shown crossed out)')
    colors = models.JSONField(default=list, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        first = self.images.first()
        return first.image if first else None

    @property
    def all_images(self):
        return self.images.all()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name} — image {self.order}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            _compress_image_field(self.image)


def _compress_image_field(image_field, max_size=(2560, 2560), quality=95):
    """
    Re-save an ImageField file as a compressed JPEG.
    Resizes to fit within *max_size* and encodes at *quality*.
    Keeps the file well under the 10 MB Anthropic API limit.
    quality=95 — максимальное качество JPEG (визуально неотличимо от оригинала).
    max_size=2560 — достаточно для любого экрана, включая 4K.
    """
    try:
        image_field.open('rb')
        img = Image.open(image_field)
        img.load()
        image_field.close()

        # Convert palette / RGBA → RGB so JPEG encoder is happy
        if img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        img.thumbnail(max_size, Image.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)

        # Overwrite the stored file in-place (no new DB row)
        image_field.storage.delete(image_field.name)
        image_field.storage.save(image_field.name, ContentFile(buffer.read()))
    except Exception as e:
        # Fix #18: Log compression failures instead of silently swallowing them
        # Never break a save because of compression failure, but always log it
        logger.warning('Image compression failed for %s: %s', image_field.name, e)
