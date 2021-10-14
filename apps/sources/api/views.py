from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models.source import Source
from core.api.views import ExtendedModelViewSet


class SourceViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing sources."""

    queryset = Source.objects.all()
    serializer_class = SourceDrfSerializer
    list_fields = None

    prefetch_relations = ExtendedModelViewSet.prefetch_relations + [
        'file',
        'tags',
        'original_edition',
    ]
