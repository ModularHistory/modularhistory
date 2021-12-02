from apps.collections.models import Collection
from apps.entities.api.serializers import EntitySerializer
from apps.entities.models.entity import Entity
from apps.propositions.api.serializers import PropositionSerializer
from apps.propositions.models.proposition import Proposition
from apps.quotes.api.serializers import QuoteSerializer
from apps.quotes.models.quote import Quote
from apps.sources.api.serializers import SourceSerializer
from apps.sources.models.source import Source
from core.models.serializers import SluggedModelSerializer


class CollectionDrfSerializer(SluggedModelSerializer):
    """Serializer for collection."""

    propositions_serialized = PropositionSerializer(
        many=True, read_only=True, source='propositions'
    )
    entities_serialized = EntitySerializer(many=True, read_only=True, source='entities')
    quotes_serialized = QuoteSerializer(many=True, read_only=True, source='quotes')
    sources_serialized = SourceSerializer(many=True, read_only=True, source='sources')

    class Meta(SluggedModelSerializer.Meta):
        model = Collection
        fields = SluggedModelSerializer.Meta.fields + [
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
