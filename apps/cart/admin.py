from django.contrib import admin
from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'session_key', 'size', 'color', 'quantity', 'added_at']
    list_filter = ['added_at']
    search_fields = ['product__name', 'session_key']
