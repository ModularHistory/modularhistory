from rest_framework import permissions
from rest_framework.generics import ListAPIView

from apps.stories.models import Story
from core.api.views import ExtendedModelViewSet


class StoryViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing stories."""

    queryset = Story.objects.all()
    # serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated]


class StoryListAPIView(ListAPIView):
    """API view for listing stories."""

    queryset = Story.objects.all()
    # serializer_class = StorySerializer
