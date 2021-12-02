from drf_writable_nested import UniqueFieldsMixin
from rest_framework.exceptions import ValidationError

from apps.sources.api.serializers import PageNumbersSerializerMixin, SourceSerializer
from apps.sources.api.sources.publication.serializers import PublicationSerializer
from apps.sources.models import Article


class _ArticleSerializer(UniqueFieldsMixin, SourceSerializer, PageNumbersSerializerMixin):
    """Serializer for article sources."""

    publication = PublicationSerializer()

    class Meta(SourceSerializer.Meta):
        model = Article
        fields = (
            SourceSerializer.Meta.fields
            + PageNumbersSerializerMixin.Meta.fields
            + [
                'publication',
                'number',
                'volume',
            ]
        )


class ArticleSerializer(_ArticleSerializer):
    """Serializer for article sources."""

    originalEdition = _ArticleSerializer(read_only=True, source='original_edition')
