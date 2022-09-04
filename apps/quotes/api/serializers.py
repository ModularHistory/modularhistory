"""Serializers for the entities app."""

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.dates.api.fields import HistoricDateTimeField, TimelinePositionField
from apps.entities.models import Entity
from apps.images.models import Image
from apps.quotes.models.quote import TEXT_MIN_LENGTH, Citation, Quote
from apps.sources.api.serializers import CitationSerializerMixin
from core.models.serializers import ModuleSerializer


class CitationSerializer(CitationSerializerMixin):
    """Serializer for quote citations."""

    class Meta(CitationSerializerMixin.Meta):
        model = Citation
        validators = [
            UniqueTogetherValidator(
                queryset=Citation.objects.all(),
                fields=['content_object', 'source', 'position'],
            )
        ]


class QuoteSerializer(WritableNestedModelSerializer, ModuleSerializer):
    """Serializer for quotes."""

    instant_search_fields = {
        'related_quotes': {'model': 'quotes.quote'},
    }

    title = serializers.CharField(required=False, allow_blank=False)
    citations = CitationSerializer(many=True, write_only=True, required=False)
    date = HistoricDateTimeField(write_only=True, required=False)
    end_date = HistoricDateTimeField(write_only=True, required=False)
    timeline_position = TimelinePositionField(read_only=True, required=False, source='date')

    def validate_text(self, value):
        if len(value) < TEXT_MIN_LENGTH:
            raise serializers.ValidationError(
                f'The quote text is too short (min_length={TEXT_MIN_LENGTH}).'
            )
        return value

    class Meta(ModuleSerializer.Meta):
        model = Quote
        fields = ModuleSerializer.Meta.fields + [
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
            'timeline_position',
        ]
        extra_kwargs = ModuleSerializer.Meta.extra_kwargs | {
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
