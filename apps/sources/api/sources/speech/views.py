from apps.sources.api.sources.speech.serializers import SpeechDrfSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Speech


class SpeechViewSet(SourceViewSet):
    """API endpoint for viewing and editing speech sources."""

    queryset = Speech.objects.all()
    serializer_class = SpeechDrfSerializer
