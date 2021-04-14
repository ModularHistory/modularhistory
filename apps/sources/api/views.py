from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.sources.models import PolymorphicSource
from apps.sources.serializers import SourceSerializer


class SourceViewSet(ModelViewSet):
    """API endpoint for viewing and editing sources."""

    queryset = PolymorphicSource.objects.all()
    serializer_class = SourceSerializer


class SourceListAPIView(ListAPIView):
    """API view for listing sources."""

    queryset = PolymorphicSource.objects.all()
    serializer_class = SourceSerializer
