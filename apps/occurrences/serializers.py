"""Serializers for the occurrences app."""

import serpy

from apps.search.api.serializers import SearchableModelSerializer


class OccurrenceSerializer(SearchableModelSerializer):
    """Serializer for occurrences."""

    dateString = serpy.StrField(attr='date_string')
    summary = serpy.StrField()
    elaboration = serpy.StrField()
    postscript = serpy.StrField()
    cachedImages = serpy.Field(attr='cached_images')
    primaryImage = serpy.Field(attr='primary_image')
    cachedCitations = serpy.Field(attr='cached_citations')
    tagsHtml = serpy.StrField(attr='tags_html')

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'occurrences.occurrence'
