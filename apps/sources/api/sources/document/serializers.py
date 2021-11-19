from apps.dates.api.fields import HistoricDateTimeDrfField
from apps.sources.api.serializers import DocumentDrfSerializerMixin, SourceDrfSerializer
from apps.sources.models import Document


class _DocumentDrfSerializer(SourceDrfSerializer, DocumentDrfSerializerMixin):
    """Serializer for document sources."""

    date = HistoricDateTimeDrfField(write_only=True, required=False)

    class Meta(SourceDrfSerializer.Meta):
        model = Document
        fields = SourceDrfSerializer.Meta.fields + DocumentDrfSerializerMixin.Meta.fields


class DocumentDrfSerializer(_DocumentDrfSerializer):
    """Serializer for document sources."""

    originalEdition = _DocumentDrfSerializer(read_only=True, source='original_edition')
