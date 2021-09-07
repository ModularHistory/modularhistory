from typing import TYPE_CHECKING

from django.conf import settings
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

from apps.flatpages.views import flatpage

if TYPE_CHECKING:
    from django.http.request import HttpRequest


class FlatPageFallbackMiddleware(MiddlewareMixin):
    """Middleware for falling back on serving a flat page matching the request URL."""

    def process_response(self, request: 'HttpRequest', response):
        if response.status_code != 404:
            return response  # No need to check for a flatpage for non-404 responses.
        try:
            return flatpage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except Exception:
            if settings.DEBUG:
                raise
            return response
