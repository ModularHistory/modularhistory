from rest_framework.generics import ListAPIView
from modularhistory.views import AsyncAPIViewMixin


class SearchResultsAPIView(AsyncAPIViewMixin, ListAPIView):
    """API view for listing search results."""

    # TODO
    ...
