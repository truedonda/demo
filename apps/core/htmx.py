"""HTMX utility helpers."""


def is_htmx(request):
    """Return True if the request was made by HTMX."""
    return request.headers.get('HX-Request') == 'true'
