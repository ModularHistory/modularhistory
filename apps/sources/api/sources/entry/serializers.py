from apps.sources.api.serializers import PageNumbersDrfSerializerMixin, SourceDrfSerializer
from apps.sources.models import Entry


class EntryDrfSerializer(SourceDrfSerializer, PageNumbersDrfSerializerMixin):
    """Serializer for journal entry sources."""

    class Meta(SourceDrfSerializer.Meta):
        model = Entry
        fields = SourceDrfSerializer.Meta.fields + PageNumbersDrfSerializerMixin.Meta.fields
