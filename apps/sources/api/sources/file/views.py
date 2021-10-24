from apps.sources.api.sources.file.serializers import SourceFileDrfSerializer
from apps.sources.models import SourceFile
from core.api.views import ExtendedModelViewSet


class SourceFileViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing sources files."""

    queryset = SourceFile.objects.all()
    serializer_class = SourceFileDrfSerializer
    list_fields = None
