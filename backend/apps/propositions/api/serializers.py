from drf_writable_nested import UniqueFieldsMixin, WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.dates.api.fields import HistoricDateTimeField, TimelinePositionField
from apps.images.models import Image
from apps.moderation.serializers import ModeratedModelSerializer
from apps.propositions.models import (
    Argument,
    ArgumentSupport,
    Citation,
    Occurrence,
    Proposition,
)
from apps.sources.api.serializers import CitationSerializerMixin
from core.models.model import ModelSerializer
from core.models.serializers import TypedModuleSerializer
from core.models.titled import TitleCaseField


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


class _PropositionSerializer(WritableNestedModelSerializer, TypedModuleSerializer):
    """Serializer for propositions."""

    date = HistoricDateTimeField(write_only=True, required=False)
    end_date = HistoricDateTimeField(write_only=True, required=False)
    citations = CitationSerializer(many=True, write_only=True, required=False)
    timeline_position = TimelinePositionField(read_only=True, required=False, source='date')

    class Meta(TypedModuleSerializer.Meta):
        model = Proposition
        fields = TypedModuleSerializer.Meta.fields + [
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
            'timeline_position',
            'type',
        ]
        read_only_fields = ['truncated_elaboration']
        extra_kwargs = TypedModuleSerializer.Meta.extra_kwargs | {
            'certainty': {'required': False},
            'images': {
                'write_only': True,
                'required': False,
                'read_only': False,
                'queryset': Image.objects.all(),
            },
        }


class ArgumentSupportSerializer(ModeratedModelSerializer):
    """Serializer for argument supports."""

    instant_search_fields = {
        'premise': {
            'model': 'propositions.proposition',
        },
    }

    class Meta(ModeratedModelSerializer.Meta):
        model = ArgumentSupport
        fields = ModeratedModelSerializer.Meta.fields + [
            # 'argument',
            'premise',
            'position',
        ]
        # TODO: needs ['argument', 'premise'], ['position', 'argument'] unique_together validators


class ArgumentSerializer(WritableNestedModelSerializer, ModeratedModelSerializer):
    """Serializer for arguments."""

    instant_search_fields = {
        'conclusion': {
            'model': 'propositions.proposition',
            'filters': {
                'type': 'propositions.conclusion',
            },
        },
        # 'premises': {
        #     'model': 'propositions.proposition',
        # },
    }

    _supports = ArgumentSupportSerializer(many=True, required=False)

    class Meta(ModeratedModelSerializer.Meta):
        model = Argument
        fields = ModeratedModelSerializer.Meta.fields + [
            'conclusion',
            'position',
            'type',
            'explanation',
            # 'premises',
            '_supports',
        ]
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

    title = TitleCaseField()
    type = serializers.HiddenField(default='propositions.occurrence')
    allowed_types = ['propositions.occurrence']

    class Meta(PropositionSerializer.Meta):
        model = Occurrence
        fields = PropositionSerializer.Meta.fields + ['postscript']
