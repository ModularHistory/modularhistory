from apps.sources.api.serializers import SourceSerializer
from apps.sources.models.source import Source
from core.api.views import ExtendedModelViewSet


class SourceViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing sources."""

    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    list_fields = None

    prefetch_relations = ExtendedModelViewSet.prefetch_relations + [
        'file',
        'tags',
        # TODO: http://modularhistory.dev.net/sources?page=3
        # Intercepted Sentry event: {'exc_info': (<class 'AttributeError'>, AttributeError("'Speech' object has no attribute 'original_edition_id'"), <traceback object at 0x7fe620380980>), 'attachments': []}
        # 'original_edition',
    ]
