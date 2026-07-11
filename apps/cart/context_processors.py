from .cart import Cart
from .wishlist import Wishlist


def cart_count(request):
    """
    Context processor that adds cart_count and wishlist_count to every template.

    Optimization: Uses a single DB query for cart items (select_related + prefetch
    is already set up in Cart.get_items). The wishlist count reads from session only
    — no DB query needed.
    """
    cart = Cart(request)
    wishlist = Wishlist(request)
    return {
        # Cart.total_items() calls get_items() which does 1 DB query with select_related
        'cart_count': cart.total_items(),
        # Wishlist.count() reads from session — zero DB queries
        'wishlist_count': wishlist.count(),
    }
