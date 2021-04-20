from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.stories.models import Story
from apps.stories.serializers import StorySerializer


class StoryViewSet(ModelViewSet):
    """API endpoint for viewing and editing stories."""

    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated]


class StoryListAPIView(ListAPIView):
    """API view for listing stories."""

    queryset = Story.objects.all()
    serializer_class = StorySerializer
