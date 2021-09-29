from apps.sources.api.serializers import SourceDrfSerializer, TextualDrfSerializerMixin
from apps.sources.models import Report


class ReportDrfSerializer(SourceDrfSerializer, TextualDrfSerializerMixin):
    """Serializer for report sources."""

    class Meta(SourceDrfSerializer.Meta):
        model = Report
        fields = (
            SourceDrfSerializer.Meta.fields
            + TextualDrfSerializerMixin.Meta.fields
            + [
                'publisher',
                'number',
            ]
        )
