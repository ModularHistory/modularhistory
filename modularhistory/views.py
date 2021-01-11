import requests
import asyncio
from asgiref.sync import sync_to_async

from django.http import JsonResponse


class AsyncAPIViewMixin:
    """
    Provides async view compatible support for DRF Views and ViewSets.

    This must be the first inherited class.  For example:
        class MyAPIViewSet(AsyncMixin, GenericViewSet):
            pass
    """

    @classmethod
    def as_view(cls, *args, **initkwargs):
        """Make Django process the view as an async view."""
        view = super().as_view(*args, **initkwargs)

        async def async_view(*args, **kwargs):
            # wait for the `dispatch` method
            return await view(*args, **kwargs)

        async_view.csrf_exempt = True
        return async_view

    async def dispatch(self, request, *args, **kwargs):
        """Add async support."""
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers
        try:
            await sync_to_async(self.initial)(request, *args, **kwargs)  # MODIFIED HERE
            if request.method.lower() in self.http_method_names:
                handler = getattr(
                    self, request.method.lower(), self.http_method_not_allowed
                )
            else:
                handler = self.http_method_not_allowed
            # accept both async and sync handlers
            # built-in handlers are sync handlers
            if not asyncio.iscoroutinefunction(handler):  # MODIFIED HERE
                handler = sync_to_async(handler)  # MODIFIED HERE
            response = await handler(request, *args, **kwargs)  # MODIFIED HERE
        except Exception as exc:
            response = self.handle_exception(exc)
        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response


class JSONResponseMixin:
    """A mixin that can be used to render a JSON response."""

    def render_to_json_response(self, context, **response_kwargs):
        """Return a JSON response, transforming 'context' to make the payload."""
        return JsonResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        """Return an object that will be serialized as JSON by json.dumps()."""
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context


def serve_from_react(request):
    # proxy requests starting with _next/
    return requests.get(f"http://dev:3000{request.get_full_path()}")
