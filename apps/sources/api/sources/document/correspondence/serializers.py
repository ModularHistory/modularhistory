from apps.dates.fields import HistoricDateTimeDrfField
from apps.sources.api.serializers import DocumentDrfSerializerMixin, SourceDrfSerializer
from apps.sources.models import CORRESPONDENCE_TYPES, Correspondence


class _CorrespondenceDrfSerializer(SourceDrfSerializer, DocumentDrfSerializerMixin):
    """Serializer for correspondence document sources."""

    date = HistoricDateTimeDrfField(write_only=True, required=False)

    def get_choices_for_field(self, field_name):
        return (x[0] for x in CORRESPONDENCE_TYPES) if field_name == 'type' else None

    class Meta(SourceDrfSerializer.Meta):
        model = Correspondence
        fields = (
            SourceDrfSerializer.Meta.fields
            + DocumentDrfSerializerMixin.Meta.fields
            + ['type', 'recipient']
        )


class CorrespondenceDrfSerializer(_CorrespondenceDrfSerializer):
    """Serializer for correspondence document sources."""

    originalEdition = _CorrespondenceDrfSerializer(read_only=True, source='original_edition')
