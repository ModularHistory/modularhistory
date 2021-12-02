from apps.propositions.api.serializers import OccurrenceSerializer
from apps.propositions.models.occurrence import Occurrence
from core.api.views import ExtendedModelViewSet


class OccurrenceViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing occurrences."""

    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceSerializer
    list_fields = ExtendedModelViewSet.list_fields | {
        'title',
        'truncated_elaboration',
        'primary_image',
    }
