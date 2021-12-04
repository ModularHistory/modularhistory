"""Serializers for the entities app."""

from drf_writable_nested import UniqueFieldsMixin, WritableNestedModelSerializer
from rest_framework import serializers

from apps.dates.api.fields import HistoricDateTimeField
from apps.dates.structures import serialize_date
from apps.entities.models import Entity
from apps.moderation.serializers import ModeratedModelSerializer
from apps.sources.api.sources.document.collection.serializers import CollectionSerializer
from apps.sources.api.sources.file.serializers import SourceFileSerializer
from apps.sources.models import AbstractCitation, Source, SourceAttribution, SourceContainment
from apps.sources.models.mixins.document import DocumentMixin
from apps.sources.models.mixins.page_numbers import PageNumbersMixin
from apps.sources.models.mixins.textual import TextualMixin
from core.models.model import ModelSerializer
from core.models.serializers import ModuleSerializer, SerializableField


class SourceAttributionSerializer(ModeratedModelSerializer):
    """Serializer for source attributions."""

    class Meta(ModeratedModelSerializer.Meta):
        model = SourceAttribution
        fields = ModeratedModelSerializer.Meta.fields + [
            # 'source',  # TODO
            'attributee',
            'position',
        ]


class SourceContainmentSerializer(ModeratedModelSerializer):
    """Serializer for source containments."""

    instant_search_fields = {'container': {'model': 'sources.source'}}

    class Meta(ModeratedModelSerializer.Meta):
        model = SourceContainment
        fields = ModeratedModelSerializer.Meta.fields + [
            'container',
            'phrase',
            'page_number',
            'end_page_number',
            'position',
        ]


class SourceSerializer(WritableNestedModelSerializer, ModuleSerializer):
    """Serializer for sources."""

    instant_search_fields = {
        'file': {'model': 'sources.sourcefile'},
    }

    title = serializers.CharField(required=False, allow_blank=False)
    date = HistoricDateTimeField(write_only=True, required=True)
    end_date = HistoricDateTimeField(write_only=True, required=False)

    attributions = SourceAttributionSerializer(many=True, required=False)
    source_containments = SourceContainmentSerializer(many=True, required=False)

    file_serialized = SourceFileSerializer(read_only=True, source='file')

    class Meta(ModuleSerializer.Meta):
        model = Source
        fields = ModuleSerializer.Meta.fields + [
            'citation_html',
            'content',
            'date',
            'end_date',
            'date_string',
            'url',
            'href',
            'file',
            'location',
            'attributee_html',
            'related_entities',
            'attributions',
            'containment_html',
            'source_containments',
            'file',
            'file_serialized',
        ]
        extra_kwargs = ModuleSerializer.Meta.extra_kwargs | {
            'citation_html': {'read_only': True},
            'content': {'write_only': True},
            'url': {'write_only': True},
            'href': {'write_only': True},
            'location': {'required': False, 'write_only': True},
            'related_entities': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Entity.objects.all(),
            },
        }


class TextualSerializerMixin(serializers.ModelSerializer):
    """TextualMixin serializer."""

    original_edition_serialized = SerializableField(read_only=True, source='original_edition')
    original_publication_date = HistoricDateTimeField(write_only=True, required=False)
    original_publication_date_serialized = serializers.SerializerMethodField(
        'get_original_publication_date', read_only=True
    )

    def get_original_publication_date(self, instance):
        return serialize_date(instance.original_publication_date)

    class Meta:
        model = TextualMixin
        fields = [
            'editors',
            'original_edition',
            'original_edition_serialized',
            'original_publication_date',
            'original_publication_date_serialized',
        ]


class PageNumbersSerializerMixin(TextualSerializerMixin):
    """PageNumbersMixin serializer."""

    class Meta(TextualSerializerMixin.Meta):
        model = PageNumbersMixin
        fields = TextualSerializerMixin.Meta.fields + [
            'page_number',
            'end_page_number',
        ]


class DocumentSerializerMixin(PageNumbersSerializerMixin):
    """DocumentMixin serializer."""

    collection_serialized = CollectionSerializer(read_only=True, source='collection')

    class Meta(PageNumbersSerializerMixin.Meta):
        model = DocumentMixin
        fields = PageNumbersSerializerMixin.Meta.fields + [
            'collection',
            'collection_serialized',
            'collection_number',
            'location_info',
            'descriptive_phrase',
            'information_url',
        ]


class CitationSerializerMixin(UniqueFieldsMixin, ModeratedModelSerializer):
    """Serializer for abstract citations."""

    instant_search_fields = {
        'source': {'model': 'sources.source'},
        'content_object': {
            'model': 'parent'  # TODO: hint that it's parent models id some way else
        },
    }

    class Meta:
        model = AbstractCitation
        fields = ModeratedModelSerializer.Meta.fields + [
            'html',
            'source',
            'citation_phrase',
            'citation_html',
            'pages',
            'position',
            'content_object',
        ]
