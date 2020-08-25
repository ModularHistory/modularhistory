from django.conf import settings
from django.contrib.flatpages.middleware import FlatpageFallbackMiddleware
from staticpages.views import staticpage
from django.http import Http404


class StaticPageFallbackMiddleware(FlatpageFallbackMiddleware):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a flatpage for non-404 responses.
        try:
            return staticpage(request, request.path_info)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            return response
        except Exception as e:
            if settings.DEBUG:
                raise e
            return response
