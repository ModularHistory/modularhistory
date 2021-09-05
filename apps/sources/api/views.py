from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models.source import Source


class SourceViewSet(ModelViewSet):
    """API endpoint for viewing and editing sources."""

    queryset = Source.objects.all()
    serializer_class = SourceDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
