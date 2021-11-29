from apps.collections.models import Collection
from apps.entities.api.serializers import EntityDrfSerializer
from apps.entities.models.entity import Entity
from apps.propositions.api.serializers import PropositionDrfSerializer
from apps.propositions.models.proposition import Proposition
from apps.quotes.api.serializers import QuoteDrfSerializer
from apps.quotes.models.quote import Quote
from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models.source import Source
from core.models.serializers import DrfSluggedModelSerializer, DrfTypedModuleSerializer


class CollectionDrfSerializer(DrfSluggedModelSerializer):
    """Serializer for collection."""

    propositions_serialized = PropositionDrfSerializer(
        many=True, read_only=True, source='propositions'
    )
    entities_serialized = EntityDrfSerializer(many=True, read_only=True, source='entities')
    quotes_serialized = QuoteDrfSerializer(many=True, read_only=True, source='quotes')
    sources_serialized = SourceDrfSerializer(many=True, read_only=True, source='sources')

    class Meta(DrfSluggedModelSerializer.Meta):
        model = Collection
        fields = DrfSluggedModelSerializer.Meta.fields + [
            'creator',
            'entities',
            'entities_serialized',
            'quotes',
            'quotes_serialized',
            'sources',
            'sources_serialized',
            'propositions',
            'propositions_serialized',
        ]
        read_only_fields = ['truncated_description']
        extra_kwargs = {
            'entities': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Entity.objects.all(),
            },
            'quotes': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Quote.objects.all(),
            },
            'sources': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Source.objects.all(),
            },
            'propositions': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Proposition.objects.all(),
            },
        }
