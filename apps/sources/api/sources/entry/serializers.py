from apps.sources.api.serializers import PageNumbersSerializerMixin, SourceSerializer
from apps.sources.models import Entry


class _EntrySerializer(SourceSerializer, PageNumbersSerializerMixin):
    """Serializer for journal entry sources."""

    class Meta(SourceSerializer.Meta):
        model = Entry
        fields = SourceSerializer.Meta.fields + PageNumbersSerializerMixin.Meta.fields


class EntrySerializer(_EntrySerializer):
    """Serializer for journal entry sources."""

    originalEdition = _EntrySerializer(read_only=True, source='original_edition')
