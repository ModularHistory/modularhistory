from apps.sources.api.serializers import PageNumbersDrfSerializerMixin, SourceDrfSerializer
from apps.sources.models import Entry


class _EntryDrfSerializer(SourceDrfSerializer, PageNumbersDrfSerializerMixin):
    """Serializer for journal entry sources."""

    instant_search_fields = SourceDrfSerializer.instant_search_fields | {
        'original_edition': {
            'model': 'sources.source',
            'filters': {'model_name': 'sources.entry'},
        },
    }

    class Meta(SourceDrfSerializer.Meta):
        model = Entry
        fields = SourceDrfSerializer.Meta.fields + PageNumbersDrfSerializerMixin.Meta.fields


class EntryDrfSerializer(_EntryDrfSerializer):
    """Serializer for journal entry sources."""

    original_edition_serialized = _EntryDrfSerializer(
        read_only=True, source='original_edition'
    )
