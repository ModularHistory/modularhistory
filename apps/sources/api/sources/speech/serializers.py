from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.search.api.instant_search import INSTANT_SEARCH_TOPICS
from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models import Speech


class SpeechDrfSerializer(SourceDrfSerializer):
    """Serializer for speech sources."""

    utterance_serialized = PropositionDrfSerializer(read_only=True, source='utterance')

    instant_search_fields = {
        'utterance': {
            'module': INSTANT_SEARCH_TOPICS,
            'filters': {
                'type': 'speech',
            },
        }
    }

    class Meta(SourceDrfSerializer.Meta):
        model = Speech
        fields = SourceDrfSerializer.Meta.fields + [
            'type',
            'audience',
            'utterance',
            'utterance_serialized',
        ]
