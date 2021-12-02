from apps.sources.api.sources.document.correspondence.serializers import (
    CorrespondenceSerializer,
)
from apps.sources.models import Correspondence
from core.api.views import ExtendedModelViewSet


class CorrespondenceViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing correspondence document sources."""

    list_fields = None
    queryset = Correspondence.objects.all()
    serializer_class = CorrespondenceSerializer
