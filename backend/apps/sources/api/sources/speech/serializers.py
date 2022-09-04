from apps.propositions.api.serializers import PropositionSerializer
from apps.sources.api.serializers import SourceSerializer
from apps.sources.models import Speech


class SpeechSerializer(SourceSerializer):
    """Serializer for speech sources."""

    utterance_serialized = PropositionSerializer(read_only=True, source='utterance')

    instant_search_fields = SourceSerializer.instant_search_fields | {
        'utterance': {
            'model': 'propositions.proposition',
            'filters': {
                'type': 'speech',
            },
        }
    }

    class Meta(SourceSerializer.Meta):
        model = Speech
        fields = SourceSerializer.Meta.fields + [
            'type',
            'audience',
            'utterance',
            'utterance_serialized',
        ]
