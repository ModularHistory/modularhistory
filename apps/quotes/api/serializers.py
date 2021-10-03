"""Serializers for the entities app."""

from drf_writable_nested import UniqueFieldsMixin, WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.dates.fields import HistoricDateTimeDrfField
from apps.entities.models import Entity
from apps.images.models import Image
from apps.quotes.models.quote import TEXT_MIN_LENGTH, Citation, Quote
from core.models.model import DrfModelSerializer
from core.models.serializers import DrfModuleSerializer


class CitationDrfSerializer(UniqueFieldsMixin, DrfModelSerializer):
    """Serializer for citations."""

    class Meta(DrfModelSerializer.Meta):
        model = Citation
        fields = DrfModelSerializer.Meta.fields + [
            'html',
            'source',
            'citation_phrase',
            'citation_html',
            'pages',
            'position',
            'content_object',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Citation.objects.all(),
                fields=['content_object', 'source', 'position'],
            )
        ]


class QuoteDrfSerializer(WritableNestedModelSerializer, DrfModuleSerializer):
    """Serializer for quotes."""

    title = serializers.CharField(required=False, allow_blank=False)
    citations = CitationDrfSerializer(many=True, write_only=True, required=False)
    date = HistoricDateTimeDrfField(write_only=True, required=False)
    end_date = HistoricDateTimeDrfField(write_only=True, required=False)

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'quotes.quote'

    def validate_text(self, value):
        if len(value) < TEXT_MIN_LENGTH:
            raise serializers.ValidationError(
                f'The quote text is too short (min_length={TEXT_MIN_LENGTH}).'
            )
        return value

    class Meta(DrfModuleSerializer.Meta):
        model = Quote
        fields = DrfModuleSerializer.Meta.fields + [
            'text',
            'pretext',
            'context',
            'bite',
            'html',
            'attributee_html',
            'attributee_string',
            'date',
            'end_date',
            'date_string',
            'primary_image',
            'cached_images',
            'citations',
            'cached_citations',
            'images',
            'attributees',
            'related_quotes',
            'related_entities',
        ]
        extra_kwargs = DrfModuleSerializer.Meta.extra_kwargs | {
            'text': {'write_only': True},
            'pretext': {'write_only': True},
            'context': {'write_only': True},
            'images': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Image.objects.all(),
            },
            'attributees': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Entity.objects.all(),
            },
            'related_quotes': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Quote.objects.all(),
            },
            'related_entities': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Entity.objects.all(),
            },
        }
