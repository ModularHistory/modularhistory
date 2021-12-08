from drf_writable_nested import UniqueFieldsMixin

from apps.sources.api.serializers import PageNumbersSerializerMixin, SourceSerializer
from apps.sources.api.sources.publication.serializers import PublicationSerializer
from apps.sources.models import Article


class _ArticleSerializer(UniqueFieldsMixin, SourceSerializer, PageNumbersSerializerMixin):
    """Serializer for article sources."""

    instant_search_fields = SourceSerializer.instant_search_fields | {
        'publication': {'model': 'sources.publication'},
        'original_edition': {
            'model': 'sources.source',
            'filters': {'model_name': 'sources.article'},
        },
    }

    publication_serialized = PublicationSerializer(read_only=True, source='publication')

    class Meta(SourceSerializer.Meta):
        model = Article
        fields = (
            SourceSerializer.Meta.fields
            + PageNumbersSerializerMixin.Meta.fields
            + [
                'publication',
                'publication_serialized',
                'number',
                'volume',
            ]
        )


class ArticleSerializer(_ArticleSerializer):
    """Serializer for article sources."""

    original_edition_serialized = _ArticleSerializer(
        read_only=True, source='original_edition'
    )
