from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models import SPEECH_TYPES, Speech


class SpeechDrfSerializer(SourceDrfSerializer):
    """Serializer for speech sources."""

    utterance_serialized = PropositionDrfSerializer(read_only=True, source='utterance')

    def get_choices_for_field(self, field_name: str):
        return (x[0] for x in SPEECH_TYPES) if field_name == 'type' else None

    class Meta(SourceDrfSerializer.Meta):
        model = Speech
        fields = SourceDrfSerializer.Meta.fields + [
            'type',
            'audience',
            'utterance',
            'utterance_serialized',
        ]
