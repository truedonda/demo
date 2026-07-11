import hashlib
from django.views.generic import ListView, DetailView
from django.db.models import Q, Min, Max
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.cache import cache
from .models import Category, Product

# ── Cache TTLs ────────────────────────────────────────────────────────────────
CATALOG_CACHE_TTL    = 60 * 10   # 10 min — filtered product list (per unique query)
PRODUCT_DETAIL_TTL   = 60 * 30   # 30 min — product + related products (DB data only)
SEARCH_CACHE_TTL     = 60 * 2    # 2 min  — live search suggestions
METADATA_CACHE_TTL   = 60 * 60   # 1 hour — sizes, colors, price bounds, categories
CATEGORIES_CACHE_TTL = 60 * 60   # 1 hour — category list (changes rarely)


# ── Shared cache helpers ───────────────────────────────────────────────────────

def _get_categories():
    """
    Return all Category objects from cache.
    Invalidated by Category post_save / post_delete signals.
    """
    key = 'catalog:categories'
    data = cache.get(key)
    if data is None:
        data = list(Category.objects.all())
        cache.set(key, data, CATEGORIES_CACHE_TTL)
    return data


def _get_catalog_metadata():
    """
    Return (price_bounds, sorted_sizes, sorted_colors) from cache or DB.
    These values are the same for all users and change only when products change.
    Invalidated by Product post_save / post_delete signals.
    """
    key = 'catalog:metadata'
    data = cache.get(key)
    if data is not None:
        return data

    all_products_qs = Product.objects.filter(is_active=True)

    price_bounds = all_products_qs.aggregate(min=Min('price'), max=Max('price'))

    all_sizes: set = set()
    all_colors: set = set()
    for sizes, colors in all_products_qs.values_list('sizes', 'colors'):
        if isinstance(sizes, list):
            all_sizes.update(sizes)
        if isinstance(colors, list):
            all_colors.update(colors)

    size_order = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'One Size']
    sorted_sizes = sorted(all_sizes, key=lambda s: size_order.index(s) if s in size_order else 99)

    color_order = ['Black', 'White', 'Grey', 'Charcoal', 'Cream', 'Beige', 'Tan',
                   'Navy', 'Pink', 'Yellow', 'Olive', 'Brown', 'Red']
    sorted_colors = sorted(all_colors, key=lambda c: color_order.index(c) if c in color_order else 99)

    data = (price_bounds, sorted_sizes, sorted_colors)
    cache.set(key, data, METADATA_CACHE_TTL)
    return data


def _catalog_queryset_cache_key(params: dict) -> str:
    """
    Build a deterministic cache key from the catalog filter params.
    Uses an MD5 hash of the sorted param string so the key stays short.
    """
    # Sort lists inside params for stable hashing
    stable = {
        k: sorted(v) if isinstance(v, list) else v
        for k, v in params.items()
    }
    raw = '|'.join(f'{k}={stable[k]}' for k in sorted(stable))
    digest = hashlib.md5(raw.encode()).hexdigest()
    return f'catalog:qs:{digest}'


def _product_detail_cache_key(slug: str) -> str:
    return f'catalog:product:{slug}'


def _search_cache_key(query: str) -> str:
    digest = hashlib.md5(query.lower().encode()).hexdigest()
    return f'catalog:search:{digest}'


# ── Views ──────────────────────────────────────────────────────────────────────

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CatalogView(ListView):
    """
    Catalog page with filtering, sorting and pagination.

    Caching strategy:
    - The filtered+sorted product list is cached per unique combination of
      filter params (hash-keyed). This is safe because the list contains no
      per-user data.
    - Metadata (sizes, colors, price bounds, categories) is cached separately
      and shared across all requests.
    - CSRF cookie is set via ensure_csrf_cookie — safe because we do NOT use
      cache_page (which would suppress Set-Cookie on cached responses).
    - in_wishlist / cart data is NOT part of this view — it lives in the
      sidebar partials which are always rendered fresh.
    """

    model = Product
    context_object_name = 'products'

    def _get_params(self) -> dict:
        GET = self.request.GET
        return {
            'category':  GET.get('category', 'all'),
            'sort':      GET.get('sort', 'newest'),
            'query':     GET.get('q', '').strip(),
            'price_min': GET.get('price_min', '').strip(),
            'price_max': GET.get('price_max', '').strip(),
            'sizes':     GET.getlist('size'),
            'colors':    GET.getlist('color'),
            'new_only':  GET.get('new_only', '') == '1',
            'in_stock':  GET.get('in_stock', '') == '1',
            'gender':    GET.get('gender', '').strip().lower(),
        }

    def _build_queryset(self, p: dict):
        """Build the filtered+sorted queryset from params."""
        qs = (Product.objects
              .filter(is_active=True)
              .select_related('category')
              .prefetch_related('images'))

        if p['category'] and p['category'] != 'all':
            qs = qs.filter(category__slug=p['category'])

        if p['gender'] in ('woman', 'man'):
            qs = qs.filter(Q(gender=p['gender']) | Q(gender='unisex'))

        if p['query']:
            qs = qs.filter(
                Q(name__icontains=p['query']) |
                Q(description__icontains=p['query']) |
                Q(category__name__icontains=p['query'])
            )

        if p['price_min']:
            try:
                qs = qs.filter(price__gte=float(p['price_min']))
            except ValueError:
                pass

        if p['price_max']:
            try:
                qs = qs.filter(price__lte=float(p['price_max']))
            except ValueError:
                pass

        if p['sizes']:
            size_q = Q()
            for s in p['sizes']:
                size_q |= Q(sizes__icontains=s)
            qs = qs.filter(size_q)

        if p['colors']:
            color_q = Q()
            for c in p['colors']:
                color_q |= Q(colors__icontains=c)
            qs = qs.filter(color_q)

        if p['new_only']:
            qs = qs.filter(is_new=True)

        if p['in_stock']:
            qs = qs.filter(stock__gt=0)

        if p['sort'] == 'price_asc':
            qs = qs.order_by('price')
        elif p['sort'] == 'price_desc':
            qs = qs.order_by('-price')
        else:
            qs = qs.order_by('-created_at')

        return qs

    def get_queryset(self):
        # Cache params and queryset on the instance to avoid re-building
        if not hasattr(self, '_params'):
            self._params = self._get_params()

        if not hasattr(self, '_queryset'):
            cache_key = _catalog_queryset_cache_key(self._params)
            cached = cache.get(cache_key)
            if cached is not None:
                self._queryset = cached
            else:
                self._queryset = list(self._build_queryset(self._params))
                cache.set(cache_key, self._queryset, CATALOG_CACHE_TTL)

        return self._queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        p = self._get_params()

        # Metadata (sizes, colors, price bounds) served from cache
        price_bounds, sorted_sizes, sorted_colors = _get_catalog_metadata()

        # Categories served from cache
        categories = _get_categories()

        # ListView already evaluated self.object_list; use len() not .count()
        product_list = context['products']
        product_count = len(product_list)

        context['categories']        = categories
        context['active_category']   = p['category']
        context['active_sort']       = p['sort']
        context['search_query']      = p['query']
        context['active_price_min']  = p['price_min']
        context['active_price_max']  = p['price_max']
        context['active_sizes']      = p['sizes']
        context['active_colors']     = p['colors']
        context['active_new_only']   = p['new_only']
        context['active_in_stock']   = p['in_stock']
        context['product_count']     = product_count
        context['price_min_bound']   = int(price_bounds['min'] or 0)
        context['price_max_bound']   = int(price_bounds['max'] or 9999)
        context['available_sizes']   = sorted_sizes
        context['available_colors']  = sorted_colors
        context['active_gender']     = p['gender']
        context['has_active_filters'] = bool(
            p['price_min'] or p['price_max'] or p['sizes'] or
            p['colors'] or p['new_only'] or p['in_stock']
        )
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            hx_target = self.request.headers.get('HX-Target', '')
            if hx_target == 'catalog-main':
                return ['catalog/partials/product_grid.html']
            return ['catalog/partials/catalog_page_content.html']
        return ['catalog/catalog.html']


class SearchSuggestView(ListView):
    """
    HTMX-powered live search suggestions panel.

    Caching strategy:
    - Results are cached per normalised query string (lowercased MD5 key).
    - TTL is short (2 min) because search results should feel fresh.
    - No per-user data in the response — safe to cache globally.
    """
    model = Product
    template_name = 'catalog/partials/search_results.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query or len(query) < 2:
            return Product.objects.none()

        cache_key = _search_cache_key(query)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        qs = list(
            Product.objects
            .filter(is_active=True)
            .filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
            .select_related('category')
            .prefetch_related('images')[:12]
        )
        cache.set(cache_key, qs, SEARCH_CACHE_TTL)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ProductDetailView(DetailView):
    """
    Product detail page.

    Caching strategy:
    - The DB-heavy part (product + related products) is cached per slug.
    - in_wishlist is per-user (session-based) — fetched fresh on every request
      and injected AFTER the cached data is retrieved.
    - ensure_csrf_cookie is safe here because we do NOT use cache_page.
    """
    model = Product
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return (Product.objects
                .filter(is_active=True)
                .select_related('category')
                .prefetch_related('images'))

    def get_object(self, queryset=None):
        slug = self.kwargs[self.slug_url_kwarg]
        cache_key = _product_detail_cache_key(slug)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        obj = super().get_object(queryset)
        cache.set(cache_key, obj, PRODUCT_DETAIL_TTL)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Related products — cached together with the product key
        related_key = f'catalog:related:{self.object.pk}'
        related = cache.get(related_key)
        if related is None:
            related = list(
                Product.objects
                .filter(category=self.object.category, is_active=True)
                .exclude(pk=self.object.pk)
                .select_related('category')
                .prefetch_related('images')[:4]
            )
            cache.set(related_key, related, PRODUCT_DETAIL_TTL)
        context['related_products'] = related

        # in_wishlist is per-user — always fetched fresh, never cached
        from apps.cart.wishlist import Wishlist
        wishlist = Wishlist(self.request)
        context['in_wishlist'] = wishlist.contains(self.object.pk)
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['catalog/partials/product_detail_content.html']
        return ['catalog/product_detail.html']

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['catalog/partials/product_detail_content.html']
        return ['catalog/product_detail.html']
