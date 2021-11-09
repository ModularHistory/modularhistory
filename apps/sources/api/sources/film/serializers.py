from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models import FILM_TYPES, Film


class FilmDrfSerializer(SourceDrfSerializer):
    """Serializer for film sources."""

    def get_choices_for_field(self, field_name):
        return (x[0] for x in FILM_TYPES) if field_name == 'type' else None

    class Meta(SourceDrfSerializer.Meta):
        model = Film
        fields = SourceDrfSerializer.Meta.fields + [
            'type',
        ]
