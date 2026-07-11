from .models import CartItem

# Fix #10: Maximum quantity per cart item
MAX_CART_ITEM_QUANTITY = 99


class Cart:
    def __init__(self, request):
        if not request.session.session_key:
            request.session.create()
        self.session_key = request.session.session_key

    def get_items(self):
        """
        Return cart items queryset with select_related + prefetch_related.
        N+1 fix: always use select_related('product') and prefetch images.
        """
        return (
            CartItem.objects
            .filter(session_key=self.session_key)
            .select_related('product')
            .prefetch_related('product__images')
        )

    def add(self, product, size='', color='', quantity=1):
        # Fix #10: Clamp quantity to max
        quantity = max(1, min(quantity, MAX_CART_ITEM_QUANTITY))
        item, created = CartItem.objects.get_or_create(
            session_key=self.session_key,
            product=product,
            size=size,
            color=color,
            defaults={'quantity': quantity},
        )
        if not created:
            new_qty = min(item.quantity + quantity, MAX_CART_ITEM_QUANTITY)
            item.quantity = new_qty
            item.save(update_fields=['quantity'])
        return item

    def remove(self, item_id):
        CartItem.objects.filter(session_key=self.session_key, pk=item_id).delete()

    def update_quantity(self, item_id, quantity):
        # Fix #10: Clamp between 1 and MAX_CART_ITEM_QUANTITY
        clamped = max(1, min(quantity, MAX_CART_ITEM_QUANTITY))
        CartItem.objects.filter(session_key=self.session_key, pk=item_id).update(quantity=clamped)

    def clear(self):
        CartItem.objects.filter(session_key=self.session_key).delete()

    def total_items(self):
        """
        N+1 fix: use aggregate COUNT instead of fetching all items.
        This avoids loading product data just to count items.
        """
        from django.db.models import Sum
        result = CartItem.objects.filter(session_key=self.session_key).aggregate(
            total=Sum('quantity')
        )
        return result['total'] or 0

    def total_price(self):
        """
        N+1 fix: compute total from already-fetched items when possible,
        or use a single DB query with annotation.
        """
        from django.db.models import F, Sum, DecimalField, ExpressionWrapper
        result = (
            CartItem.objects
            .filter(session_key=self.session_key)
            .select_related('product')
            .aggregate(
                total=Sum(
                    ExpressionWrapper(
                        F('quantity') * F('product__price'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    )
                )
            )
        )
        return result['total'] or 0

    def get_items_with_total(self):
        """
        N+1 fix: Return (items, total_price) in a single DB query.
        Use this in views that need both items and total to avoid calling
        get_items() and total_price() separately (which would be 2 queries).
        """
        items = list(self.get_items())
        total = sum(item.subtotal for item in items)
        return items, total
