"""Serializers for the occurrences app."""

import serpy

from apps.search.models.searchable_model import SearchableModelSerializer


class OccurrenceSerializer(SearchableModelSerializer):
    """Serializer for occurrences."""

    dateHtml = serpy.Field(attr='date_html')
    summary = serpy.Field(attr='summary.html')
    description = serpy.Field(attr='description.html')
    postscript = serpy.MethodField()
    serializedImages = serpy.Field(attr='serialized_images')
    primaryImage = serpy.Field(attr='primary_image')
    serializedCitations = serpy.Field(attr='serialized_citations')
    tagsHtml = serpy.Field(attr='tags_html')

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'occurrences.occurrence'

    def get_postscript(self, instance):
        """Return the user-facing postscript HTML."""
        return instance.postscript.html if instance.postscript else ''
