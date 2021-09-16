from rest_framework import permissions

from apps.propositions.api.serializers import OccurrenceDrfSerializer
from apps.propositions.models.occurrence import Occurrence
from core.api.views import ExtendedModelViewSet


class OccurrenceViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing occurrences."""

    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceDrfSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    list_fields = ExtendedModelViewSet.list_fields + ['title', 'truncated_elaboration', 'primary_image']
