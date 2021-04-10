import logging

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.template.base import Template
from pympler import classtracker, muppy, tracker

PYMPLER_ENABLED = False

class PymplerMiddleware:
    """Run Pympler (memory profiler)."""

    memory_tracker: tracker.SummaryTracker
    class_tracker: classtracker.ClassTracker
    object_count: int

    def __init__(self, get_response):
        """Construct and configure the middleware, one time."""
        if PYMPLER_ENABLED and not settings.DEBUG:
            self.memory_tracker = tracker.SummaryTracker()
            self.class_tracker = classtracker.ClassTracker()
            self.class_tracker.track_class(Template)
            self.object_count = len(muppy.get_objects())
            self.get_response = get_response
        else:
            raise MiddlewareNotUsed('PymplerMiddleware will not be used.')

    def __call__(self, request):
        """Run the middleware."""
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        self.class_tracker.create_snapshot()

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called:
        self.memory_tracker.print_diff()
        object_count = len(muppy.get_objects())
        logging.info(f'{object_count} objects')

        self.class_tracker.create_snapshot()
        self.class_tracker.stats.print_summary()

        return response
