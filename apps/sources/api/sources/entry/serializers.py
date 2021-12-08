from apps.sources.api.serializers import PageNumbersSerializerMixin, SourceSerializer
from apps.sources.models import Entry


class _EntrySerializer(SourceSerializer, PageNumbersSerializerMixin):
    """Serializer for journal entry sources."""

    instant_search_fields = SourceSerializer.instant_search_fields | {
        'original_edition': {
            'model': 'sources.source',
            'filters': {'model_name': 'sources.entry'},
        },
    }

    class Meta(SourceSerializer.Meta):
        model = Entry
        fields = SourceSerializer.Meta.fields + PageNumbersSerializerMixin.Meta.fields


class EntrySerializer(_EntrySerializer):
    """Serializer for journal entry sources."""

    original_edition_serialized = _EntrySerializer(read_only=True, source='original_edition')
