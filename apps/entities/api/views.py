from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.entities.api.serializers import EntityModelSerializer
from apps.entities.models.entity import Entity
from apps.search.documents.entity import EntityDocument


class EntityViewSet(ModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntityModelSerializer
    permission_classes = [permissions.AllowAny]


class EntityInstantSearchAPIView(APIView):
    """API view used by search-as-you-type fields retrieving entity names and IDs."""

    def get(self, request):
        query = request.query_params.get('query', '')
        if len(query) == 0:
            return Response([])
        results = (
            EntityDocument.search()
            .query('match', name__instant_search=query)
            .extra(_source=['name'])
        )
        return Response([{'id': result.meta.id} | result.to_dict() for result in results])
