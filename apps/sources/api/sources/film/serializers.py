from apps.sources.api.serializers import SourceSerializer
from apps.sources.models import Film


class FilmSerializer(SourceSerializer):
    """Serializer for film sources."""

    class Meta(SourceSerializer.Meta):
        model = Film
        fields = SourceSerializer.Meta.fields + [
            'type',
        ]
