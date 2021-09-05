from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.topics.api.serializers import TopicModelSerializer
from apps.topics.models.topic import Topic
from core.pagination import VariableSizePagination


class TopicViewSet(ModelViewSet):
    """API endpoint for viewing and editing topics."""

    queryset = Topic.objects.all()
    lookup_field = 'slug'
    serializer_class = TopicModelSerializer
    pagination_class = VariableSizePagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
