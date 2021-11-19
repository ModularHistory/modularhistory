import serpy

from apps.dates.fields import TimelinePositionField
from core.models.module import ModuleSerializer


class _PropositionSerializer(ModuleSerializer):
    """Serializer for propositions."""

    summary = serpy.StrField()
    elaboration = serpy.StrField()
    truncated_elaboration = serpy.StrField()
    certainty = serpy.IntField(required=False)
    date_string = serpy.StrField()
    cached_images = serpy.Field()
    primary_image = serpy.Field()
    cached_citations = serpy.Field()
    tags_html = serpy.StrField()
    timeline_position = TimelinePositionField(attr='date', required=False)


class ArgumentSerializer(serpy.Serializer):
    """Serializer for arguments."""

    explanation = serpy.StrField()
    premises = _PropositionSerializer(many=True, attr='premises.all', call=True)


class PropositionSerializer(_PropositionSerializer):
    """Serializer for propositions."""

    arguments = ArgumentSerializer(many=True, attr='arguments.all', call=True)


class OccurrenceSerializer(PropositionSerializer):
    """Serializer for occurrences."""

    postscript = serpy.StrField()
