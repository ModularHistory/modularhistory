from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.search.documents import TopicInstantSearchDocument
from apps.topics.api.serializers import TopicDrfSerializer
from apps.topics.models.topic import Topic
from core.api.views import ExtendedModelViewSet
from core.pagination import VariableSizePagination


class TopicViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing topics."""

    queryset = Topic.objects.all()
    serializer_class = TopicDrfSerializer
    pagination_class = VariableSizePagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    list_fields = {'name', 'id'}


class TopicInstantSearchAPIView(APIView):
    """API view used by search-as-you-type fields retrieving topic names and IDs."""

    def get(self, request):
        query = request.query_params.get('query', '')
        if len(query) == 0:
            return Response([])
        results = (
            TopicInstantSearchDocument.search()
            .query('multi_match', query=query)
            .source(['name'])
        )
        return Response([{'id': result.meta.id} | result.to_dict() for result in results])
