"""Serializers for the entities app."""
from rest_framework import serializers

from apps.dates.fields import HistoricDateTimeDrfField
from apps.entities.models import Entity
from apps.sources.models import Source, SourceContainment
from core.models.model import DrfModelSerializer
from core.models.serializers import DrfModuleSerializer


class SourceDrfSerializer(DrfModuleSerializer):
    """Serializer for sources."""

    save_after_m2m_update = True

    title = serializers.CharField(required=False, allow_blank=False)
    date = HistoricDateTimeDrfField(write_only=True, required=True)
    end_date = HistoricDateTimeDrfField(write_only=True, required=False)

    def get_model(self, instance) -> str:
        """Return the model name of the instance."""
        return 'sources.source'

    class Meta(DrfModuleSerializer.Meta):
        model = Source
        fields = DrfModuleSerializer.Meta.fields + [
            'citation_html',
            'content',
            'date',
            'date_string',
            'url',
            'href',
            'file',
            'attributee_html',
            'attributees',
            'related_entities',
            'containment_html',
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


class ContainmentDrfSerializer(DrfModelSerializer):
    """Serializer for source containments."""

    container = SourceDrfSerializer()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'sources.sourcecontainment'

    class Meta(DrfModelSerializer.Meta):
        model = SourceContainment
        fields = DrfModelSerializer.Meta.fields + [
            'phrase',
            'page_number',
            'end_page_number',
            'container',
        ]
