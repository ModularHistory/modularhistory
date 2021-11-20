from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from ..documents import instant_search_documents_map
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


class InstantSearchApiView(APIView):
    """API view used by search-as-you-type fields."""

    def get(self, request):
        query = request.query_params.get(QUERY_PARAM) or request.data.get(QUERY_PARAM, '')
        model = request.query_params.get('model') or request.data.get('model')
        filters = request.data.get('filters', {})

        if model not in instant_search_documents_map:
            raise ValidationError(
                f'Invalid instant search model, must be one of: {", ".join(instant_search_documents_map.keys())}'
            )
        if not isinstance(filters, dict):
            raise ValidationError(f'Invalid filters, must be a key-valued object')

        if len(query) == 0:
            return Response([])

        document = instant_search_documents_map[model]
        search = document.search()

        if filters:
            search = search.filter('term', **filters)

        results = search.query(
            'multi_match', query=query, fields=document.search_fields
        ).source(document.search_fields)

        return Response([{'id': result.meta.id} | result.to_dict() for result in results])
