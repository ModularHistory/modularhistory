from apps.sources.api.serializers import DocumentSerializerMixin, SourceSerializer
from apps.sources.models import Affidavit


class _AffidavitSerializer(SourceSerializer, DocumentSerializerMixin):
    """Serializer for affidavit document sources."""

    instant_search_fields = (
        SourceSerializer.instant_search_fields
        | DocumentSerializerMixin.instant_search_fields
        | {
            'original_edition': {
                'model': 'sources.source',
                'filters': {'model_name': 'sources.affidavit'},
            },
        }
    )

    class Meta(SourceSerializer.Meta):
        location_required = True
        model = Affidavit
        fields = (
            SourceSerializer.Meta.fields + DocumentSerializerMixin.Meta.fields + ['certifier']
        )
        extra_kwargs = SourceSerializer.Meta.extra_kwargs | {
            'location': {'required': True, 'write_only': True}
        }


class AffidavitSerializer(_AffidavitSerializer):
    """Serializer for affidavit document sources."""

    original_edition_serialized = _AffidavitSerializer(
        read_only=True, source='original_edition'
    )
