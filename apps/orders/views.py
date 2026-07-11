import logging
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.urls import reverse
from apps.cart.cart import Cart
from apps.core.htmx import is_htmx
from .forms import OrderForm
from .models import Order, OrderItem

logger = logging.getLogger(__name__)


class CheckoutView(View):
    def get(self, request):
        cart = Cart(request)
        # N+1 fix: single query for both items and total
        items, total = cart.get_items_with_total()
        context = {
            'form': OrderForm(),
            'cart_items': items,
            'cart_total': total,
            'cart_empty': not items,
        }
        if is_htmx(request):
            return render(request, 'orders/partials/checkout_content.html', context)
        return render(request, 'orders/checkout.html', context)

    def post(self, request):
        cart = Cart(request)
        # N+1 fix: single query for both items and total
        items, total = cart.get_items_with_total()
        form = OrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)

            # Fix #17: Compute total server-side and assert > 0
            if not total or total <= 0:
                context = {
                    'form': form,
                    'cart_items': items,
                    'cart_total': total,
                    'cart_empty': True,
                }
                if is_htmx(request):
                    return render(request, 'orders/partials/checkout_content.html', context)
                return render(request, 'orders/checkout.html', context)

            order.total_price = total
            order.payment_status = Order.PAYMENT_PENDING
            parts = []
            if form.cleaned_data.get('region'):
                parts.append(form.cleaned_data['region'])
            if form.cleaned_data.get('city'):
                parts.append(form.cleaned_data['city'])
            if form.cleaned_data.get('branch'):
                parts.append(form.cleaned_data['branch'])
            order.address = ', '.join(parts) if parts else ''
            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.size,
                    color=item.color,
                    quantity=item.quantity,
                    price_snapshot=item.product.price,
                )

            cart.clear()

            # Fix #5: Store order PK in session so only the creator can access payment pages
            request.session['last_order_pk'] = order.pk

            url = reverse('orders:payment_pending', kwargs={'pk': order.pk})
            if is_htmx(request):
                response = HttpResponse()
                response['HX-Redirect'] = url
                return response
            return redirect(url)

        context = {
            'form': form,
            'cart_items': items,
            'cart_total': total,
            'cart_empty': False,
        }
        if is_htmx(request):
            return render(request, 'orders/partials/checkout_content.html', context)
        return render(request, 'orders/checkout.html', context)


class PaymentPendingView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        # Fix #5: Verify the session created this order
        if request.session.get('last_order_pk') != order.pk:
            logger.warning(
                'Unauthorized payment_pending access: session=%s order_pk=%s',
                request.session.session_key, pk
            )
            raise Http404
        context = {'order': order}
        if is_htmx(request):
            return render(request, 'orders/partials/payment_pending_content.html', context)
        return render(request, 'orders/payment_pending.html', context)


class PaymentSuccessView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        # Fix #5: Verify the session created this order
        if request.session.get('last_order_pk') != order.pk:
            logger.warning(
                'Unauthorized payment_success access: session=%s order_pk=%s',
                request.session.session_key, pk
            )
            raise Http404
        order.payment_status = Order.PAYMENT_PAID
        order.status = Order.STATUS_CONFIRMED
        order.save(update_fields=['payment_status', 'status'])
        context = {'order': order}
        if is_htmx(request):
            return render(request, 'orders/partials/payment_success_content.html', context)
        return render(request, 'orders/payment_success.html', context)


class PaymentFailedView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        # Fix #5: Verify the session created this order
        if request.session.get('last_order_pk') != order.pk:
            logger.warning(
                'Unauthorized payment_failed access: session=%s order_pk=%s',
                request.session.session_key, pk
            )
            raise Http404
        order.payment_status = Order.PAYMENT_FAILED
        order.save(update_fields=['payment_status'])
        context = {'order': order}
        if is_htmx(request):
            return render(request, 'orders/partials/payment_failed_content.html', context)
        return render(request, 'orders/payment_failed.html', context)
