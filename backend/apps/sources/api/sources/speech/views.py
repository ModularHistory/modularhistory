from apps.sources.api.sources.speech.serializers import SpeechSerializer
from apps.sources.api.views import SourceViewSet
from apps.sources.models import Speech


class SpeechViewSet(SourceViewSet):
    """API endpoint for viewing and editing speech sources."""

    queryset = Speech.objects.all()
    serializer_class = SpeechSerializer
