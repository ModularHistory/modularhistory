from apps.collections.models import Collection
from apps.entities.api.serializers import EntityDrfSerializer
from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.quotes.api.serializers import QuoteDrfSerializer
from apps.sources.api.serializers import SourceDrfSerializer
from core.models.serializers import DrfTypedModuleSerializer


class CollectionDrfSerializer(DrfTypedModuleSerializer):
    """Serializer for collection."""

    propositions = PropositionDrfSerializer(many=True)
    entities = EntityDrfSerializer(many=True)
    quotes = QuoteDrfSerializer(many=True)
    sources = SourceDrfSerializer(many=True)

    class Meta(DrfTypedModuleSerializer.Meta):
        model = Collection
        fields = DrfTypedModuleSerializer.Meta.fields + [
            'creator',
            'entities',
            'quotes',
            'sources',
            'propositions',
        ]
        fields.remove('tags')
        read_only_fields = ['truncated_description']
