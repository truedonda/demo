from django.urls import path
from .views import AccountView, LoginView, RegisterView, LogoutView

app_name = 'accounts'

urlpatterns = [
    path('account/', AccountView.as_view(), name='account'),
    path('account/login/', LoginView.as_view(), name='login'),
    path('account/register/', RegisterView.as_view(), name='register'),
    path('account/logout/', LogoutView.as_view(), name='logout'),
]
