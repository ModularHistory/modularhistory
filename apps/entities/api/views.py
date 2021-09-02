from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.search.documents.entity import EntityDocument

from apps.entities.serializers import EntitySerializer
from apps.entities.api.serializers_drf import EntitySerializerDrf
from apps.entities.models.entity import Entity


class EntityViewSet(ModelViewSet):
    """API endpoint for viewing and editing entities."""

    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore
    serializer_class = EntitySerializerDrf


class EntityListAPIView(ListAPIView):
    """API view for listing entities."""

    permission_classes = [permissions.AllowAny]
    serializer_class = EntitySerializer
    queryset = Entity.objects.exclude(type='entities.deity').order_by('birth_date')  # type: ignore


class EntityInstantSearchAPIView(APIView):
    """API view used by search-as-you-type fields retrieving entity names and IDs."""

    def get(self, request):
        query = request.query_params.get('query', '')
        if len(query) == 0:
            return Response([])
        results = EntityDocument.search().query('match', name__instant_search=query).extra(_source=['name'])
        return Response([{'id': result.meta.id} | result.to_dict() for result in results])
