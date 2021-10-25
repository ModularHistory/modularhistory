import serpy

from core.models.module import ModuleSerializer


class _PropositionSerializer(ModuleSerializer):
    """Serializer for propositions."""

    summary = serpy.StrField()
    elaboration = serpy.StrField()
    certainty = serpy.IntField(required=False)
    date_string = serpy.StrField()
    cached_images = serpy.Field()
    primary_image = serpy.Field()
    cached_citations = serpy.Field()
    tags_html = serpy.StrField()


class ArgumentSerializer(serpy.Serializer):
    """Serializer for arguments."""

    explanation = serpy.StrField()
    premises = _PropositionSerializer(many=True, attr='premises.all', call=True)


class PropositionSerializer(_PropositionSerializer):
    """Serializer for propositions."""

    summary = serpy.StrField()
    elaboration = serpy.StrField()
    certainty = serpy.IntField(required=False)
    date_string = serpy.StrField()
    cached_images = serpy.Field()
    primary_image = serpy.Field()
    cached_citations = serpy.Field()
    tags_html = serpy.StrField()
    arguments = ArgumentSerializer(many=True, attr='arguments.all', call=True)


class OccurrenceSerializer(PropositionSerializer):
    """Serializer for occurrences."""

    postscript = serpy.StrField()
