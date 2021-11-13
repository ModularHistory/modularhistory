from drf_writable_nested import UniqueFieldsMixin
from rest_framework.exceptions import ValidationError

from apps.sources.api.serializers import PageNumbersDrfSerializerMixin, SourceDrfSerializer
from apps.sources.api.sources.publication.serializers import PublicationDrfSerializer
from apps.sources.models import Article


class _ArticleDrfSerializer(
    UniqueFieldsMixin, SourceDrfSerializer, PageNumbersDrfSerializerMixin
):
    """Serializer for article sources."""

    publication = PublicationDrfSerializer()

    class Meta(SourceDrfSerializer.Meta):
        model = Article
        fields = (
            SourceDrfSerializer.Meta.fields
            + PageNumbersDrfSerializerMixin.Meta.fields
            + [
                'publication',
                'number',
                'volume',
            ]
        )


class ArticleDrfSerializer(_ArticleDrfSerializer):
    """Serializer for article sources."""

    originalEdition = _ArticleDrfSerializer(read_only=True, source='original_edition')
