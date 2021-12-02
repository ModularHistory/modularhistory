from drf_writable_nested import UniqueFieldsMixin, WritableNestedModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from apps.dates.api.fields import HistoricDateTimeDrfField, TimelinePositionDrfField
from apps.images.models import Image
from apps.propositions.models import Argument, Citation, Occurrence, Proposition
from apps.sources.api.serializers import CitationSerializerMixin
from core.models.model import DrfModelSerializer
from core.models.serializers import DrfTypedModuleSerializer
from core.models.titled import TitleCaseDrfField


class CitationSerializer(CitationSerializerMixin):
    """Serializer for proposition citations."""

    class Meta(CitationSerializerMixin.Meta):
        model = Citation
        validators = [
            UniqueTogetherValidator(
                queryset=Citation.objects.all(),
                fields=['content_object', 'source', 'position'],
            )
        ]


class _PropositionSerializer(WritableNestedModelSerializer, DrfTypedModuleSerializer):
    """Serializer for propositions."""

    date = HistoricDateTimeDrfField(write_only=True, required=False)
    end_date = HistoricDateTimeDrfField(write_only=True, required=False)
    citations = CitationSerializer(many=True, write_only=True, required=False)
    timeline = TimelinePositionDrfField(read_only=True, required=False, source='date')

    class Meta(DrfTypedModuleSerializer.Meta):
        model = Proposition
        fields = DrfTypedModuleSerializer.Meta.fields + [
            'summary',
            'elaboration',
            'truncated_elaboration',
            'certainty',
            'date',
            'end_date',
            'date_string',
            'tags_html',
            'citations',
            'cached_citations',
            'images',
            'primary_image',
            'cached_images',
            'timeline',
        ]
        read_only_fields = ['truncated_elaboration']
        extra_kwargs = DrfTypedModuleSerializer.Meta.extra_kwargs | {
            'certainty': {'required': False},
            'images': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Image.objects.all(),
            },
        }


class ArgumentSerializer(UniqueFieldsMixin, DrfModelSerializer):
    """Serializer for arguments."""

    premises_serialized = _PropositionSerializer(
        many=True, read_only=True, source='premises.all'
    )

    class Meta:
        model = Argument
        fields = DrfModelSerializer.Meta.fields + [
            'conclusion',
            'position',
            'type',
            'explanation',
            'premises',
            'premises_serialized',
        ]
        extra_kwargs = {
            'premises': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Proposition.objects.all(),
            }
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Argument.objects.all(),
                fields=['conclusion', 'position'],
            )
        ]


class PropositionSerializer(_PropositionSerializer):
    """Serializer for propositions."""

    arguments = ArgumentSerializer(many=True, required=False)

    class Meta(_PropositionSerializer.Meta):
        model = Proposition
        fields = _PropositionSerializer.Meta.fields + ['arguments']


class OccurrenceSerializer(PropositionSerializer):
    """Serializer for occurrences."""

    title = TitleCaseDrfField()

    class Meta(PropositionSerializer.Meta):
        model = Occurrence
        fields = PropositionSerializer.Meta.fields + ['postscript']
        allowed_types = ['propositions.occurrence']
