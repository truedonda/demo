from django.urls import path
from .views import (
    CartDetailView, CartAddView, CartUpdateView, CartRemoveView, CartCountView,
    WishlistDetailView, WishlistToggleView, WishlistRemoveView, WishlistCountView,
)

app_name = 'cart'

urlpatterns = [
    path('', CartDetailView.as_view(), name='detail'),
    path('add/', CartAddView.as_view(), name='add'),
    path('update/<int:item_id>/', CartUpdateView.as_view(), name='update'),
    # Fix #8: Changed from DELETE to POST for proper CSRF protection
    path('remove/<int:item_id>/', CartRemoveView.as_view(), name='remove'),
    path('count/', CartCountView.as_view(), name='count'),
    # Wishlist
    path('wishlist/', WishlistDetailView.as_view(), name='wishlist_detail'),
    path('wishlist/toggle/', WishlistToggleView.as_view(), name='wishlist_toggle'),
    path('wishlist/remove/<int:product_id>/', WishlistRemoveView.as_view(), name='wishlist_remove'),
    path('wishlist/count/', WishlistCountView.as_view(), name='wishlist_count'),
]
