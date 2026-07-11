from django.urls import path
from .views import CheckoutView, PaymentPendingView, PaymentSuccessView, PaymentFailedView

app_name = 'orders'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<int:pk>/pending/', PaymentPendingView.as_view(), name='payment_pending'),
    path('payment/<int:pk>/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/<int:pk>/failed/', PaymentFailedView.as_view(), name='payment_failed'),
]
