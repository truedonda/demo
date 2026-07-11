from django.views import View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from apps.catalog.models import Product
from .cart import Cart
from .wishlist import Wishlist, WISHLIST_SESSION_KEY


class CartDetailView(View):
    def get(self, request):
        cart = Cart(request)
        # N+1 fix: single query for both items and total
        items, total = cart.get_items_with_total()
        context = {
            'cart_items': items,
            'cart_total': total,
        }
        html = render_to_string('cart/partials/cart_sidebar.html', context, request=request)
        return HttpResponse(html)


class CartAddView(View):
    def post(self, request):
        cart = Cart(request)
        product_id = request.POST.get('product_id')
        size = request.POST.get('size', '')
        color = request.POST.get('color', '')
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        cart.add(product=product, size=size, color=color)

        # N+1 fix: single query for items + total
        items, total = cart.get_items_with_total()
        context = {
            'cart_items': items,
            'cart_total': total,
            'cart_count': sum(i.quantity for i in items),
        }
        response = HttpResponse(render_to_string('cart/partials/cart_sidebar.html', context, request=request))
        response['HX-Trigger'] = 'cartUpdated'
        return response


class CartUpdateView(View):
    def post(self, request, item_id):
        cart = Cart(request)
        quantity = int(request.POST.get('quantity', 1))
        cart.update_quantity(item_id, quantity)

        # N+1 fix: single query for items + total
        items, total = cart.get_items_with_total()
        context = {
            'cart_items': items,
            'cart_total': total,
            'cart_count': sum(i.quantity for i in items),
        }
        response = HttpResponse(render_to_string('cart/partials/cart_sidebar.html', context, request=request))
        response['HX-Trigger'] = 'cartUpdated'
        return response


# Fix #8: Changed from DELETE to POST for proper CSRF protection
class CartRemoveView(View):
    def post(self, request, item_id):
        cart = Cart(request)
        cart.remove(item_id)

        # N+1 fix: single query for items + total
        items, total = cart.get_items_with_total()
        context = {
            'cart_items': items,
            'cart_total': total,
            'cart_count': sum(i.quantity for i in items),
        }
        response = HttpResponse(render_to_string('cart/partials/cart_sidebar.html', context, request=request))
        response['HX-Trigger'] = 'cartUpdated'
        return response


class CartCountView(View):
    def get(self, request):
        cart = Cart(request)
        # N+1 fix: total_items() uses aggregate COUNT — no product data loaded
        html = render_to_string('cart/partials/cart_count.html', {'cart_count': cart.total_items()}, request=request)
        return HttpResponse(html)


class WishlistDetailView(View):
    def get(self, request):
        wishlist = Wishlist(request)
        products = wishlist.get_products()
        html = render_to_string('cart/partials/wishlist_sidebar.html', {'wishlist_products': products}, request=request)
        return HttpResponse(html)


class WishlistToggleView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        wishlist = Wishlist(request)
        added = wishlist.toggle(product.pk)
        products = wishlist.get_products()
        html = render_to_string('cart/partials/wishlist_sidebar.html', {'wishlist_products': products}, request=request)
        response = HttpResponse(html)
        response['HX-Trigger'] = 'wishlistUpdated'
        return response


class WishlistRemoveView(View):
    def post(self, request, product_id):
        wishlist = Wishlist(request)
        wishlist.remove(product_id)
        products = wishlist.get_products()
        html = render_to_string('cart/partials/wishlist_sidebar.html', {'wishlist_products': products}, request=request)
        response = HttpResponse(html)
        response['HX-Trigger'] = 'wishlistUpdated'
        return response


class WishlistCountView(View):
    def get(self, request):
        wishlist = Wishlist(request)
        count = wishlist.count()
        html = render_to_string('cart/partials/wishlist_count.html', {'wishlist_count': count}, request=request)
        return HttpResponse(html)
