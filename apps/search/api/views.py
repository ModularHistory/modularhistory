from rest_framework.generics import ListAPIView

from .filters.elastic_filters import ModulesSearchFilterBackend
from .filters.post_resolve_filters import ApplyMetaFilterBackend, SortByFilterBackend
from .filters.pre_resolve_filters import PreResolveFilterBackend
from .pagination import ElasticPageNumberPagination
from .search import Search

QUERY_PARAM = 'query'


class SearchResultsSerializer:
    """Serializer for search results."""

    def __init__(self, queryset, *args, **kwargs):
        self.data = [instance.serialize() for instance in queryset]


class ElasticSearchResultsAPIView(ListAPIView):
    serializer_class = SearchResultsSerializer
    pagination_class = ElasticPageNumberPagination

    # These filters are applied to the ES search instance.
    filter_backends = [ModulesSearchFilterBackend]

    # These filters are applied during resolving.
    pre_resolve_filters = [PreResolveFilterBackend]

    # These filters are applied after the search results resolved to models
    # applying meta filter backend should be first because sort and future
    # filters might depend on meta field.
    post_resolve_filters = [ApplyMetaFilterBackend, SortByFilterBackend]

    suppress_unverified: bool
    search: Search

    def get_queryset(self):
        self.search = Search()

        return self.search
