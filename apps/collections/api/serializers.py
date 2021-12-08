from apps.collections.models import Collection
from apps.entities.api.serializers import EntitySerializer
from apps.propositions.api.serializers import PropositionSerializer
from apps.quotes.api.serializers import QuoteSerializer
from apps.sources.api.serializers import SourceSerializer
from core.models.serializers import SluggedModelSerializer


class CollectionSerializer(SluggedModelSerializer):
    """Serializer for collection."""

    propositions = PropositionSerializer(many=True)
    entities = EntitySerializer(many=True)
    quotes = QuoteSerializer(many=True)
    sources = SourceSerializer(many=True)

    class Meta(SluggedModelSerializer.Meta):
        model = Collection
        fields = SluggedModelSerializer.Meta.fields + [
            'creator',
            'entities',
            'quotes',
            'sources',
            'propositions',
        ]
        read_only_fields = ['truncated_description']
