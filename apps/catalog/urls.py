from django.urls import path
from .views import CatalogView, ProductDetailView, SearchSuggestView

app_name = 'catalog'

urlpatterns = [
    path('shop/', CatalogView.as_view(), name='catalog'),
    path('search/suggest/', SearchSuggestView.as_view(), name='search_suggest'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]
