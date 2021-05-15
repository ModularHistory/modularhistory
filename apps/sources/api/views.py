from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.sources.models.source import Source
from apps.sources.serializers import SourceSerializer


class SourceViewSet(ModelViewSet):
    """API endpoint for viewing and editing sources."""

    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class SourceListAPIView(ListAPIView):
    """API view for listing sources."""

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
