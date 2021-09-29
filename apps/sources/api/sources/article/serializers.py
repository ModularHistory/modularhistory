from apps.sources.api.serializers import PageNumbersDrfSerializerMixin, SourceDrfSerializer
from apps.sources.models import Article


class ArticleDrfSerializer(SourceDrfSerializer, PageNumbersDrfSerializerMixin):
    """Serializer for article sources."""

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
