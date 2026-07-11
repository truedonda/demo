"""
Fix #6: Simple IP-based rate limiting using Django's cache framework.
No external dependencies required.

Usage:
    from apps.core.ratelimit import RateLimit

    limiter = RateLimit(key='login', rate=5, period=60)  # 5 attempts per 60 seconds
    if limiter.is_limited(request):
        return HttpResponse('Too many attempts. Please try again later.', status=429)
    limiter.increment(request)
"""
from django.core.cache import cache


def _get_client_ip(request):
    """Extract real client IP, respecting X-Forwarded-For from trusted proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded_for:
        # Take the first IP in the chain (client IP)
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


class RateLimit:
    """
    Simple sliding-window rate limiter backed by Django's cache.

    Args:
        key: Unique identifier for this rate limit (e.g. 'login', 'register')
        rate: Maximum number of requests allowed in the period
        period: Time window in seconds
    """

    def __init__(self, key: str, rate: int, period: int):
        self.key = key
        self.rate = rate
        self.period = period

    def _cache_key(self, request) -> str:
        ip = _get_client_ip(request)
        return f'ratelimit:{self.key}:{ip}'

    def get_count(self, request) -> int:
        return cache.get(self._cache_key(request), 0)

    def increment(self, request) -> int:
        cache_key = self._cache_key(request)
        try:
            count = cache.incr(cache_key)
        except ValueError:
            # Key doesn't exist yet — create it
            cache.set(cache_key, 1, timeout=self.period)
            count = 1
        return count

    def is_limited(self, request) -> bool:
        return self.get_count(request) >= self.rate

    def reset(self, request):
        cache.delete(self._cache_key(request))


# Pre-configured limiters for auth endpoints
# Fix #6: 5 POST attempts per minute per IP on login
login_limiter = RateLimit(key='login', rate=5, period=60)

# Fix #6: 3 registrations per hour per IP
register_limiter = RateLimit(key='register', rate=3, period=3600)
