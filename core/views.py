import asyncio

from asgiref.sync import sync_to_async
from concurrency.views import ConflictResponse
from diff_match_patch import diff_match_patch
from django.http import JsonResponse
from django.template import loader
from django.template.context import RequestContext
from django.utils.safestring import mark_safe


def get_diff(current, stored):
    data = []
    dmp = diff_match_patch()
    fields = current._meta.fields
    for field in fields:
        v1 = getattr(current, field.name, '')
        v2 = getattr(stored, field.name, '')
        diff = dmp.diff_main(unicode(v1), unicode(v2))
        dmp.diff_cleanupSemantic(diff)
        html = dmp.diff_prettyHtml(diff)
        html = mark_safe(html)
        data.append((field, v1, v2, html))
    return data


def conflict(request, target=None, template_name='409.html'):
    template = loader.get_template(template_name)
    try:
        saved = target.__class__._default_manager.get(pk=target.pk)
        diff = get_diff(target, saved)
    except target.__class__.DoesNotExists:
        saved = None
        diff = None

    ctx = RequestContext(
        request,
        {'target': target, 'diff': diff, 'saved': saved, 'request_path': request.path},
    )
    return ConflictResponse(template.render(ctx))


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
