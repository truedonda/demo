from django.db import models
from apps.catalog.models import Product


class CartItem(models.Model):
    session_key = models.CharField(max_length=40)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session_key', 'product', 'size', 'color']
        ordering = ['added_at']

    def __str__(self):
        return f'{self.product.name} x{self.quantity} ({self.size})'

    @property
    def subtotal(self):
        return self.product.price * self.quantity
