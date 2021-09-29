from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models import Speech


class SpeechDrfSerializer(SourceDrfSerializer):
    """Serializer for speech sources."""

    class Meta(SourceDrfSerializer.Meta):
        model = Speech
        fields = SourceDrfSerializer.Meta.fields + ['type', 'audience', 'utterance']
