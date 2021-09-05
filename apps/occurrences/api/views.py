from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from apps.propositions.api.serializers import OccurrenceDrfSerializer
from apps.propositions.models.occurrence import Occurrence


class OccurrenceViewSet(ModelViewSet):
    """API endpoint for viewing and editing occurrences."""

    queryset = Occurrence.objects.all()
    lookup_field = 'slug'
    serializer_class = OccurrenceDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
