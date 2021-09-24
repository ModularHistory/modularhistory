from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.collections.models import Collections
from apps.propositions.api.serializers import OccurrenceDrfSerializer


class CollectionsViewSet(ModelViewSet):
    """API endpoint for viewing and editing occurrences."""

    queryset = Collections.objects.all()
    lookup_field = 'slug'
    serializer_class = OccurrenceDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
