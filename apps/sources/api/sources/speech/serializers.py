from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models import SPEECH_TYPES, Speech


class SpeechDrfSerializer(SourceDrfSerializer):
    """Serializer for speech sources."""

    utterance_serialized = PropositionDrfSerializer(read_only=True, source='utterance')

    type_field_choices = SPEECH_TYPES

    class Meta(SourceDrfSerializer.Meta):
        model = Speech
        fields = SourceDrfSerializer.Meta.fields + [
            'type',
            'audience',
            'utterance',
            'utterance_serialized',
        ]
