from drf_writable_nested import UniqueFieldsMixin
from rest_framework import serializers

from apps.dates.api.fields import HistoricDateTimeField
from apps.sources.api.serializers import SourceSerializer, TextualSerializerMixin
from apps.sources.models import Webpage, Website
from apps.sources.models.publication import AbstractPublication, Publication
from core.models.model import ModelSerializer, TypedModelSerializer


class PublicationMixinSerializer(serializers.ModelSerializer):
    """Serializer for abstract publication sources."""

    class Meta:
        model = AbstractPublication
        fields = ['name', 'aliases', 'description']


class PublicationSerializer(
    UniqueFieldsMixin,
    TypedModelSerializer,
    PublicationMixinSerializer,
):
    """Serializer for publication sources."""

    class Meta(SourceSerializer.Meta):
        model = Publication
        fields = TypedModelSerializer.Meta.fields + PublicationMixinSerializer.Meta.fields


class _WebpageSerializer(SourceSerializer, TextualSerializerMixin):
    """Serializer for webpage sources."""

    date = HistoricDateTimeField(write_only=True, required=False)

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


class WebsiteSerializer(ModelSerializer, PublicationMixinSerializer):
    """Serializer for website sources."""

    class Meta:
        model = Website
        fields = PublicationMixinSerializer.Meta.fields + ['owner']
