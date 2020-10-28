from django.conf import settings
from django.contrib.flatpages.middleware import FlatpageFallbackMiddleware
from django.http import Http404

from staticpages.views import staticpage

HTTP404_RESPONSE_CODE = 404


class StaticPageFallbackMiddleware(FlatpageFallbackMiddleware):
    """TODO: add docstring."""

    def process_response(self, request, response):
        """Attempt to fall back on a static page."""
        if response.status_code != HTTP404_RESPONSE_CODE:
            return response
        try:
            return staticpage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except Exception as error:
            if settings.DEBUG:
                raise error
            return response
