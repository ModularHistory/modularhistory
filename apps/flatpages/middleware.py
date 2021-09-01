from django.conf import settings
from django.contrib.flatpages.middleware import FlatpageFallbackMiddleware
from django.http import Http404

from apps.flatpages.views import flatpage

HTTP404_RESPONSE_CODE = 404


class FlatPageFallbackMiddleware(FlatpageFallbackMiddleware):
    """
    Override FlatpageFallbackMiddleware to use our flatpage view.

    This middleware tries to serve a static page matching the request URL,
    if no code-defined URL patterns matched the request.
    """

    def process_response(self, request, response):
        """Attempt to fall back on a static page."""
        if response.status_code != HTTP404_RESPONSE_CODE:
            return response
        try:
            return flatpage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except Exception as error:
            if settings.DEBUG:
                raise error
            return response
