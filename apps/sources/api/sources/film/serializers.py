from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models import Film


class FilmDrfSerializer(SourceDrfSerializer):
    """Serializer for film sources."""

    class Meta(SourceDrfSerializer.Meta):
        model = Film
        fields = SourceDrfSerializer.Meta.fields + [
            'type',
        ]
