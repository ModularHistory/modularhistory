from apps.sources.api.sources.document.affidavit.serializers import AffidavitDrfSerializer
from apps.sources.models import Affidavit
from core.api.views import ExtendedModelViewSet


class AffidavitViewSet(ExtendedModelViewSet):
    """API endpoint for viewing and editing affidavit document sources."""

    list_fields = None
    queryset = Affidavit.objects.all()
    serializer_class = AffidavitDrfSerializer
