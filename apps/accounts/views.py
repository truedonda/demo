from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from apps.core.htmx import is_htmx
from apps.core.ratelimit import login_limiter, register_limiter
from apps.cart.models import CartItem


def htmx_redirect(url):
    """Return an empty 200 response with HX-Redirect header for HTMX requests."""
    from django.http import HttpResponse
    response = HttpResponse()
    response['HX-Redirect'] = url
    return response


def _safe_next(request):
    """Fix #4: Validate next URL to prevent open redirect attacks."""
    raw = request.POST.get('next') or request.GET.get('next') or ''
    if raw and url_has_allowed_host_and_scheme(raw, allowed_hosts={request.get_host()}):
        return raw
    return reverse('accounts:account')


class AccountView(TemplateView):
    def get(self, request, *args, **kwargs):
        if is_htmx(request):
            return render(request, 'accounts/partials/account_content.html')
        return render(request, 'accounts/account.html')


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if is_htmx(request):
                return htmx_redirect(reverse('accounts:account'))
            return redirect('accounts:account')
        if is_htmx(request):
            return render(request, 'accounts/partials/login_content.html')
        return render(request, 'accounts/login.html')

    def post(self, request):
        # Fix #6: Rate limit login attempts — 5 per minute per IP
        if login_limiter.is_limited(request):
            context = {'error': 'Too many login attempts. Please wait a minute and try again.'}
            if is_htmx(request):
                return render(request, 'accounts/partials/login_content.html', context)
            return render(request, 'accounts/login.html', context)
        login_limiter.increment(request)

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Fix #9: Save old session key before login() rotates it
            old_session_key = request.session.session_key

            login(request, user)

            # Fix #9: Migrate cart items from old session to new session
            new_session_key = request.session.session_key
            if old_session_key and new_session_key and old_session_key != new_session_key:
                CartItem.objects.filter(session_key=old_session_key).update(
                    session_key=new_session_key
                )

            next_url = _safe_next(request)
            if is_htmx(request):
                return htmx_redirect(next_url)
            return redirect(next_url)

        context = {
            'error': 'Invalid username or password.',
            'username': username,
        }
        if is_htmx(request):
            return render(request, 'accounts/partials/login_content.html', context)
        return render(request, 'accounts/login.html', context)


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if is_htmx(request):
                return htmx_redirect(reverse('accounts:account'))
            return redirect('accounts:account')
        if is_htmx(request):
            return render(request, 'accounts/partials/register_content.html')
        return render(request, 'accounts/register.html')

    def post(self, request):
        # Fix #6: Rate limit registration — 3 per hour per IP
        if register_limiter.is_limited(request):
            context = {'errors': {'__all__': 'Too many registration attempts. Please try again later.'}}
            if is_htmx(request):
                return render(request, 'accounts/partials/register_content.html', context)
            return render(request, 'accounts/register.html', context)
        register_limiter.increment(request)

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = {}

        if not username:
            errors['username'] = 'Username is required.'
        elif User.objects.filter(username=username).exists():
            # Fix #7: Generic message — don't reveal if username exists
            errors['username'] = 'This username is not available.'

        if not email:
            errors['email'] = 'Email is required.'
        elif User.objects.filter(email=email).exists():
            # Fix #7: Generic message — don't reveal if email is registered
            errors['email'] = 'Unable to register with this email address.'

        if not password1:
            errors['password1'] = 'Password is required.'
        elif len(password1) < 8:
            errors['password1'] = 'Password must be at least 8 characters.'
        elif password1 != password2:
            errors['password2'] = 'Passwords do not match.'

        if errors:
            context = {
                'errors': errors,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'username': username,
            }
            if is_htmx(request):
                return render(request, 'accounts/partials/register_content.html', context)
            return render(request, 'accounts/register.html', context)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )

        # Fix #9: Save old session key before login() rotates it
        old_session_key = request.session.session_key
        login(request, user)
        new_session_key = request.session.session_key
        if old_session_key and new_session_key and old_session_key != new_session_key:
            CartItem.objects.filter(session_key=old_session_key).update(
                session_key=new_session_key
            )

        if is_htmx(request):
            return htmx_redirect(reverse('accounts:account'))
        return redirect('accounts:account')


class LogoutView(View):
    def post(self, request):
        logout(request)
        if is_htmx(request):
            return htmx_redirect(reverse('catalog:catalog'))
        return redirect('catalog:catalog')
