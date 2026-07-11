from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'size', 'color', 'quantity', 'price_snapshot']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['total_price', 'created_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Customer', {'fields': ('full_name', 'email', 'phone', 'address')}),
        ('Order Info', {'fields': ('total_price', 'status', 'created_at')}),
    )
