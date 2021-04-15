from rest_framework import permissions
from rest_framework.generics import ListAPIView
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
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class TopicPartialAPIView(ListAPIView):
    """API view for listing selected topic attributes."""

    permission_classes = [permissions.AllowAny]
    queryset = Topic.objects.values("pk", "key")
    serializer_class = TopicDictSerializer
    pagination_class = VariableSizePagination
