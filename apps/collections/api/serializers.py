from apps.collections.models import Collection
from apps.entities.api.serializers import EntityDrfSerializer
from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.quotes.api.serializers import QuoteDrfSerializer
from apps.sources.api.serializers import SourceDrfSerializer
from core.models.serializers import DrfSluggedModelSerializer


class CollectionDrfSerializer(DrfSluggedModelSerializer):
    """Serializer for collection."""

    propositions = PropositionDrfSerializer(many=True)
    entities = EntityDrfSerializer(many=True)
    quotes = QuoteDrfSerializer(many=True)
    sources = SourceDrfSerializer(many=True)

    class Meta(DrfSluggedModelSerializer.Meta):
        model = Collection
        fields = DrfSluggedModelSerializer.Meta.fields + [
            'creator',
            'entities',
            'quotes',
            'sources',
            'propositions',
        ]
        read_only_fields = ['truncated_description']
