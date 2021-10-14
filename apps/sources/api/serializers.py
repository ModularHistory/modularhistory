"""Serializers for the entities app."""
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from apps.dates.fields import HistoricDateTimeDrfField
from apps.dates.structures import serialize_date
from apps.entities.models import Entity
from apps.sources.api.sources.document.collection.serializers import CollectionDrfSerializer
from apps.sources.api.sources.file.serializers import SourceFileDrfSerializer
from apps.sources.models import Source, SourceContainment
from apps.sources.models.mixins.document import DocumentMixin
from apps.sources.models.mixins.page_numbers import PageNumbersMixin
from apps.sources.models.mixins.textual import TextualMixin
from core.models.model import DrfModelSerializer
from core.models.serializers import DrfModuleSerializer, SerializableDrfField


class SourceContainmentDrfSerializer(DrfModelSerializer):
    """Serializer for source containments."""

    class Meta(DrfModelSerializer.Meta):
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

    source_containments = SourceContainmentDrfSerializer(
        many=True, write_only=True, required=False
    )
    file_serialized = SourceFileDrfSerializer(read_only=True, source='file')

    class Meta(DrfModuleSerializer.Meta):
        model = Source
        # TODO: missing `file` field
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
            'attributees',
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
            'attributees': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Entity.objects.all(),
            },
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
    originalPublicationDate = serializers.SerializerMethodField(
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
            'originalPublicationDate',
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
