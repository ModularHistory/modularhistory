from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.topics.models.topic import Topic
from apps.topics.serializers import TopicSerializer
from core.pagination import VariableSizePagination


class TopicViewSet(ModelViewSet):
    """API endpoint for viewing and editing topics."""

    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class TopicListAPIView(ListAPIView):
    """API view for listing topics."""

    permission_classes = [permissions.AllowAny]
    pagination_class = VariableSizePagination
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class TopicAPIView(RetrieveAPIView):
    """API view for a single occurrences."""

    queryset = Topic.objects.all()
    lookup_field = 'slug'
    serializer_class = TopicSerializer
