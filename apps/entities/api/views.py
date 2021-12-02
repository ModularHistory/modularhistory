from rest_framework.response import Response
from rest_framework.views import APIView

from apps.entities.api.serializers import EntitySerializer
from apps.entities.models.entity import Entity
from apps.search.documents.entity import EntityInstantSearchDocument
from core.api.views import ExtendedModelViewSet


class EntityViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializer
    list_fields = ExtendedModelViewSet.list_fields | {
        'title',
        'truncated_description',
        'primary_image',
    }


class EntityInstantSearchAPIView(APIView):
    """API view used by search-as-you-type fields retrieving entity names and IDs."""

    def get(self, request):
        query = request.query_params.get('query', '')
        if len(query) == 0:
            return Response([])
        results = (
            EntityInstantSearchDocument.search()
            .query('multi_match', query=query)
            .source(['name'])
        )
        return Response([{'id': result.meta.id} | result.to_dict() for result in results])
