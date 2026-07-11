from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    # Fix #19: Admin at non-guessable URL (change 'cozy-admin-2026' to something secret in production)
    path('cozy-admin-2026/', admin.site.urls),

    path('', TemplateView.as_view(template_name='splash.html'), name='splash'),
    path('', include('apps.catalog.urls', namespace='catalog')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('', include('apps.accounts.urls', namespace='accounts')),

    # Fix #26: Serve favicon.ico to stop 404 noise in logs
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),

    # Fix #24: robots.txt — prevent crawlers from indexing admin/cart/orders
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt',
        content_type='text/plain',
    )),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar — only in DEBUG mode
    # Uncomment to re-enable:
    # import debug_toolbar
    # urlpatterns = [
    #     path('__debug__/', include(debug_toolbar.urls)),
    # ] + urlpatterns
