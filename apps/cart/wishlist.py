from apps.catalog.models import Product

WISHLIST_SESSION_KEY = 'wishlist'

# Fix #11: Maximum wishlist size to prevent session bloat DoS
MAX_WISHLIST_SIZE = 100


class Wishlist:
    def __init__(self, request):
        self.session = request.session
        if WISHLIST_SESSION_KEY not in self.session:
            self.session[WISHLIST_SESSION_KEY] = []
        self.product_ids = self.session[WISHLIST_SESSION_KEY]

    def add(self, product_id):
        product_id = int(product_id)
        # Fix #11: Enforce size limit
        if product_id not in self.product_ids and len(self.product_ids) < MAX_WISHLIST_SIZE:
            self.product_ids.append(product_id)
            self.session.modified = True

    def remove(self, product_id):
        product_id = int(product_id)
        if product_id in self.product_ids:
            self.product_ids.remove(product_id)
            self.session.modified = True

    def toggle(self, product_id):
        product_id = int(product_id)
        if product_id in self.product_ids:
            self.remove(product_id)
            return False
        else:
            self.add(product_id)
            return True

    def contains(self, product_id):
        return int(product_id) in self.product_ids

    def get_products(self):
        # N+1 fix: add select_related('category') to avoid per-product category queries
        return Product.objects.filter(
            pk__in=self.product_ids, is_active=True
        ).select_related('category').prefetch_related('images')

    def count(self):
        return len(self.product_ids)
