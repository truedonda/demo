"""
Cache invalidation signals for the catalog app.

When a Product or Category is saved or deleted in the admin (or via code),
we must bust the relevant Redis cache keys so stale data is never served.

Keys invalidated:
  catalog:metadata          — price bounds, sizes, colors
  catalog:categories        — category list
  catalog:qs:*              — all filtered product-list results (pattern delete)
  catalog:search:*          — all search suggestion results (pattern delete)
  catalog:product:<slug>    — individual product detail
  catalog:related:<pk>      — related products for a product
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

logger = logging.getLogger(__name__)


def _delete_pattern(pattern: str) -> None:
    """
    Delete all Redis keys matching *pattern* (glob-style).
    Uses django-redis's delete_pattern() which calls SCAN + DEL.
    Falls back to cache.clear() for LocMemCache (local dev) — safe because
    LocMemCache is process-local and only used in development.
    """
    try:
        deleted = cache.delete_pattern(pattern)
        logger.debug('Cache invalidation: deleted %s keys matching "%s"', deleted, pattern)
    except AttributeError:
        # LocMemCache / DummyCache don't have delete_pattern — clear all local cache
        cache.clear()
        logger.debug('Cache backend does not support delete_pattern, cleared all cache (pattern: "%s")', pattern)


def _invalidate_product_caches(product) -> None:
    """Bust all caches that depend on product data."""
    # Shared metadata (price bounds, sizes, colors)
    cache.delete('catalog:metadata')

    # All filtered catalog queryset results
    _delete_pattern('*catalog:qs:*')

    # All search suggestion results
    _delete_pattern('*catalog:search:*')

    # This specific product's detail page
    cache.delete(f'catalog:product:{product.slug}')

    # Related products for this product
    cache.delete(f'catalog:related:{product.pk}')

    # Related products for OTHER products in the same category
    # (they include this product in their "related" list)
    if product.category_id:
        from .models import Product as ProductModel
        sibling_pks = (
            ProductModel.objects
            .filter(category_id=product.category_id, is_active=True)
            .exclude(pk=product.pk)
            .values_list('pk', flat=True)
        )
        keys = [f'catalog:related:{pk}' for pk in sibling_pks]
        if keys:
            cache.delete_many(keys)


def _invalidate_category_caches() -> None:
    """Bust all caches that depend on category data."""
    cache.delete('catalog:categories')
    cache.delete('catalog:metadata')
    _delete_pattern('*catalog:qs:*')
    _delete_pattern('*catalog:search:*')


# ── Product signals ────────────────────────────────────────────────────────────

@receiver(post_save, sender='catalog.Product')
def on_product_save(sender, instance, **kwargs):
    _invalidate_product_caches(instance)


@receiver(post_delete, sender='catalog.Product')
def on_product_delete(sender, instance, **kwargs):
    _invalidate_product_caches(instance)


# ── Category signals ───────────────────────────────────────────────────────────

@receiver(post_save, sender='catalog.Category')
def on_category_save(sender, instance, **kwargs):
    _invalidate_category_caches()


@receiver(post_delete, sender='catalog.Category')
def on_category_delete(sender, instance, **kwargs):
    _invalidate_category_caches()
