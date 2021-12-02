from apps.dates.api.fields import HistoricDateTimeField
from apps.sources.api.serializers import DocumentSerializerMixin, SourceSerializer
from apps.sources.models import Document


class _DocumentSerializer(SourceSerializer, DocumentSerializerMixin):
    """Serializer for document sources."""

    date = HistoricDateTimeField(write_only=True, required=False)

    class Meta(SourceSerializer.Meta):
        model = Document
        fields = SourceSerializer.Meta.fields + DocumentSerializerMixin.Meta.fields


class DocumentSerializer(_DocumentSerializer):
    """Serializer for document sources."""

    originalEdition = _DocumentSerializer(read_only=True, source='original_edition')
