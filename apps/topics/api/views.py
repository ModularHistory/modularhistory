from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.topics.models import Topic
from apps.topics.serializers import TopicDictSerializer, TopicSerializer
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


class TopicPartialAPIView(ListAPIView):
    """API view for listing selected topic attributes."""

    permission_classes = [permissions.AllowAny]
    queryset = Topic.objects.values('pk', 'name')
    serializer_class = TopicDictSerializer
    pagination_class = VariableSizePagination


class TopicAPIView(RetrieveAPIView):
    """API view for a single occurrences."""

    queryset = Topic.objects.all()
    lookup_field = 'slug'
    serializer_class = TopicSerializer
