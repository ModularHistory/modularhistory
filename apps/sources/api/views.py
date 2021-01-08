from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from modularhistory.views import AsyncAPIViewMixin
from apps.sources.serializers import SourceSerializer

from apps.sources.models import Source


class SourceViewSet(ModelViewSet):
    """API endpoint for viewing and editing sources."""

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    permission_classes = [permissions.IsAuthenticated]


class SourceListAPIView(AsyncAPIViewMixin, ListAPIView):
    """API view for listing sources."""

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
