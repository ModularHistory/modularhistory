from drf_writable_nested import UniqueFieldsMixin
from rest_framework import serializers

from apps.dates.api.fields import HistoricDateTimeDrfField
from apps.sources.api.serializers import SourceSerializer, TextualSerializerMixin
from apps.sources.models import Webpage, Website
from apps.sources.models.publication import AbstractPublication, Publication
from core.models.model import DrfModelSerializer, DrfTypedModelSerializer


class PublicationDrfMixinSerializer(serializers.ModelSerializer):
    """Serializer for abstract publication sources."""

    class Meta:
        model = AbstractPublication
        fields = ['name', 'aliases', 'description']


class PublicationSerializer(
    UniqueFieldsMixin,
    DrfTypedModelSerializer,
    PublicationDrfMixinSerializer,
):
    """Serializer for publication sources."""

    class Meta(SourceSerializer.Meta):
        model = Publication
        fields = (
            DrfTypedModelSerializer.Meta.fields + PublicationDrfMixinSerializer.Meta.fields
        )


class _WebpageSerializer(SourceSerializer, TextualSerializerMixin):
    """Serializer for webpage sources."""

    date = HistoricDateTimeDrfField(write_only=True, required=False)

    def validate(self, attrs):
        if not attrs.get('website') and not attrs.get('website_name'):
            raise serializers.ValidationError(
                'Please specify either `website` or `website_name`.'
            )
        return attrs

    class Meta(SourceSerializer.Meta):
        model = Webpage
        fields = (
            SourceSerializer.Meta.fields
            + TextualSerializerMixin.Meta.fields
            + [
                'website_name',
                'website',
            ]
        )


class WebpageSerializer(_WebpageSerializer):
    """Serializer for webpage sources."""

    originalEdition = _WebpageSerializer(read_only=True, source='original_edition')


class WebsiteSerializer(DrfModelSerializer, PublicationDrfMixinSerializer):
    """Serializer for website sources."""

    class Meta:
        model = Website
        fields = PublicationDrfMixinSerializer.Meta.fields + ['owner']
