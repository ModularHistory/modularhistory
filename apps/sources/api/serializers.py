"""Serializers for the entities app."""

from drf_writable_nested import UniqueFieldsMixin, WritableNestedModelSerializer
from rest_framework import serializers

from apps.dates.api.fields import HistoricDateTimeDrfField
from apps.dates.structures import serialize_date
from apps.entities.models import Entity
from apps.sources.api.sources.document.collection.serializers import CollectionDrfSerializer
from apps.sources.api.sources.file.serializers import SourceFileDrfSerializer
from apps.sources.models import AbstractCitation, Source, SourceAttribution, SourceContainment
from apps.sources.models.mixins.document import DocumentMixin
from apps.sources.models.mixins.page_numbers import PageNumbersMixin
from apps.sources.models.mixins.textual import TextualMixin
from core.models.model import DrfModelSerializer
from core.models.serializers import DrfModuleSerializer, SerializableDrfField


class SourceAttributionDrfSerializer(DrfModelSerializer):
    """Serializer for source attributions."""

    class Meta:
        model = SourceAttribution
        fields = DrfModelSerializer.Meta.fields + [
            # 'source',  # TODO
            'attributee',
        ]


class SourceContainmentDrfSerializer(DrfModelSerializer):
    """Serializer for source containments."""

    class Meta:
        model = SourceContainment
        fields = DrfModelSerializer.Meta.fields + [
            'source',
            'container',
            'phrase',
            'page_number',
            'end_page_number',
            'position',
        ]


class SourceDrfSerializer(WritableNestedModelSerializer, DrfModuleSerializer):
    """Serializer for sources."""

    title = serializers.CharField(required=False, allow_blank=False)
    date = HistoricDateTimeDrfField(write_only=True, required=True)
    end_date = HistoricDateTimeDrfField(write_only=True, required=False)

    attributions = SourceAttributionDrfSerializer(many=True)
    source_containments = SourceContainmentDrfSerializer(many=True, required=False)

    file_serialized = SourceFileDrfSerializer(read_only=True, source='file')

    class Meta(DrfModuleSerializer.Meta):
        model = Source
        fields = DrfModuleSerializer.Meta.fields + [
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
            'attributions',
            'related_entities',
            'containment_html',
            'source_containments',
            'file',
            'file_serialized',
        ]
        extra_kwargs = DrfModuleSerializer.Meta.extra_kwargs | {
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


class TextualDrfSerializerMixin(serializers.ModelSerializer):
    """TextualMixin serializer."""

    originalEdition = SerializableDrfField(read_only=True, source='original_edition')
    original_publication_date = HistoricDateTimeDrfField(write_only=True, required=False)
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
            'originalEdition',
            'original_publication_date',
            'original_publication_date_serialized',
        ]


class PageNumbersDrfSerializerMixin(TextualDrfSerializerMixin):
    """PageNumbersMixin serializer."""

    class Meta(TextualDrfSerializerMixin.Meta):
        model = PageNumbersMixin
        fields = TextualDrfSerializerMixin.Meta.fields + [
            'page_number',
            'end_page_number',
        ]


class DocumentDrfSerializerMixin(PageNumbersDrfSerializerMixin):
    """DocumentMixin serializer."""

    collection_serialized = CollectionDrfSerializer(read_only=True, source='collection')

    class Meta(PageNumbersDrfSerializerMixin.Meta):
        model = DocumentMixin
        fields = PageNumbersDrfSerializerMixin.Meta.fields + [
            'collection',
            'collection_serialized',
            'collection_number',
            'location_info',
            'descriptive_phrase',
            'information_url',
        ]


class CitationDrfSerializerMixin(UniqueFieldsMixin, DrfModelSerializer):
    """Serializer for abstract citations."""

    class Meta:
        model = AbstractCitation
        fields = DrfModelSerializer.Meta.fields + [
            'html',
            'source',
            'citation_phrase',
            'citation_html',
            'pages',
            'position',
            'content_object',
        ]
