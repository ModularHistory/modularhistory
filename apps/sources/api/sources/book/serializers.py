from apps.sources.api.serializers import SourceDrfSerializer, TextualDrfSerializerMixin
from apps.sources.models import Book, Section


class _BookDrfSerializer(SourceDrfSerializer, TextualDrfSerializerMixin):
    """Serializer for book sources."""

    class Meta(SourceDrfSerializer.Meta):
        model = Book
        fields = (
            SourceDrfSerializer.Meta.fields
            + TextualDrfSerializerMixin.Meta.fields
            + [
                'translator',
                'publisher',
                'edition_year',
                'edition_number',
                'printing_number',
                'volume_number',
            ]
        )


class BookDrfSerializer(_BookDrfSerializer):
    """Serializer for book sources."""

    originalEdition = _BookDrfSerializer(read_only=True, source='original_edition')


class SectionDrfSerializer(SourceDrfSerializer):
    """Serializer for book section sources."""

    class Meta(SourceDrfSerializer.Meta):
        model = Section
        fields = SourceDrfSerializer.Meta.fields + ['type', 'work']
