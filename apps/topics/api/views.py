from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.topics.models import Topic
from apps.topics.serializers import TopicSerializer


class TopicViewSet(ModelViewSet):
    """API endpoint for viewing and editing topics."""

    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]


class TopicListAPIView(ListAPIView):
    """API view for listing topics."""

    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
