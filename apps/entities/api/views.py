from typing import Type

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.entities.api.serializers import EntityDrfSerializer
from apps.entities.models.entity import Entity
from apps.search.documents.base import InstantSearchDocument
from apps.search.documents.entity import EntityInstantSearchDocument
from core.api.views import ExtendedModelViewSet


class EntityViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntityDrfSerializer
    list_fields = ExtendedModelViewSet.list_fields | {
        'title',
        'truncated_description',
        'primary_image',
    }


class InstantSearchApiView(APIView):
    """Abstract API view used by search-as-you-type endpoints."""

    document: Type[InstantSearchDocument]

    def get(self, request):
        query = request.query_params.get('query', '')
        if len(query) == 0:
            return Response([])

        search = self.document.search()
        if request.query_params.get('filters', None):
            search = search.filter('term', **request.query_params.get('filters', {}))

        results = search.query(
            'multi_match', query=query, fields=self.document.search_fields
        ).source(self.document.search_fields)

        return Response([{'id': result.meta.id} | result.to_dict() for result in results])


class EntityInstantSearchAPIView(InstantSearchApiView):
    document = EntityInstantSearchDocument
