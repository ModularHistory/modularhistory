from rest_framework import permissions
from core.api.views import ExtendedModelViewSet

from apps.propositions.api.serializers import OccurrenceDrfSerializer
from apps.propositions.models.occurrence import Occurrence


class OccurrenceViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing occurrences."""

    queryset = Occurrence.objects.all()
    lookup_field = 'slug'
    serializer_class = OccurrenceDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
