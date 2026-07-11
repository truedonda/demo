from django.db import models
from django.core.validators import RegexValidator
from apps.catalog.models import Product

# Fix #16: Phone number validator
_phone_validator = RegexValidator(
    regex=r'^\+?[\d\s\-\(\)]{7,20}$',
    message='Введіть коректний номер телефону (7–20 цифр, допускаються +, пробіли, дефіси, дужки).'
)


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
    ]

    PAYMENT_PENDING = 'pending'
    PAYMENT_PAID = 'paid'
    PAYMENT_FAILED = 'failed'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_FAILED, 'Failed'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    # Fix #16: Phone number validation
    phone = models.CharField(max_length=30, validators=[_phone_validator])
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    comment = models.TextField(blank=True)
    address = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} — {self.full_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField()
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.product.name if self.product else "Deleted"} x{self.quantity}'

    @property
    def subtotal(self):
        return self.price_snapshot * self.quantity
