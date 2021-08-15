import serpy

from apps.search.api.serializers import SearchableModelSerializer


class _PropositionSerializer(SearchableModelSerializer):
    """Serializer for propositions."""

    summary = serpy.StrField()
    elaboration = serpy.StrField()
    certainty = serpy.IntField(required=False)
    dateString = serpy.StrField(attr='date_string')
    cachedImages = serpy.Field(attr='cached_images')
    primaryImage = serpy.Field(attr='primary_image')
    cachedCitations = serpy.Field(attr='cached_citations')
    tagsHtml = serpy.StrField(attr='tags_html')

    def get_model(self, instance) -> str:
        """Return the model name of serialized propositions."""
        return 'propositions.proposition'


class ArgumentSerializer(serpy.Serializer):
    """Serializer for arguments."""

    explanation = serpy.StrField()
    premises = _PropositionSerializer(many=True, attr='premises.all', call=True)


class PropositionSerializer(_PropositionSerializer):
    """Serializer for propositions."""

    summary = serpy.StrField()
    elaboration = serpy.StrField()
    certainty = serpy.IntField(required=False)
    dateString = serpy.StrField(attr='date_string')
    cachedImages = serpy.Field(attr='cached_images')
    primaryImage = serpy.Field(attr='primary_image')
    cachedCitations = serpy.Field(attr='cached_citations')
    tagsHtml = serpy.StrField(attr='tags_html')
    arguments = ArgumentSerializer(many=True, attr='arguments.all', call=True)

    def get_model(self, instance) -> str:
        """Return the model name of serialized propositions."""
        return 'propositions.proposition'


class OccurrenceSerializer(PropositionSerializer):
    """Serializer for occurrences."""

    postscript = serpy.StrField()

    def get_model(self, instance) -> str:
        """Return the model name of the instance."""
        return 'propositions.occurrence'
