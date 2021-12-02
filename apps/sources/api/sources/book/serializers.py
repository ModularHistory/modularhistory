from apps.sources.api.serializers import SourceSerializer, TextualSerializerMixin
from apps.sources.models import Book, Section


class _BookSerializer(SourceSerializer, TextualSerializerMixin):
    """Serializer for book sources."""

    class Meta(SourceSerializer.Meta):
        model = Book
        fields = (
            SourceSerializer.Meta.fields
            + TextualSerializerMixin.Meta.fields
            + [
                'translator',
                'publisher',
                'edition_year',
                'edition_number',
                'printing_number',
                'volume_number',
            ]
        )


class BookSerializer(_BookSerializer):
    """Serializer for book sources."""

    originalEdition = _BookSerializer(read_only=True, source='original_edition')


class SectionSerializer(SourceSerializer):
    """Serializer for book section sources."""

    class Meta(SourceSerializer.Meta):
        model = Section
        fields = SourceSerializer.Meta.fields + ['type', 'work']
