from apps.sources.api.serializers import SourceDrfSerializer
from apps.sources.models import FILM_TYPES, Film


class FilmDrfSerializer(SourceDrfSerializer):
    """Serializer for film sources."""

    type_field_choices = FILM_TYPES

    class Meta(SourceDrfSerializer.Meta):
        model = Film
        fields = SourceDrfSerializer.Meta.fields + [
            'type',
        ]
