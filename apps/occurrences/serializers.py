"""Serializers for the occurrences app."""

import serpy

from apps.search.api.serializers import SearchableModelSerializer


class OccurrenceSerializer(SearchableModelSerializer):
    """Serializer for occurrences."""

    dateHtml = serpy.Field(attr='date_html')
    summary = serpy.Field(attr='summary.html')
    elaboration = serpy.Field(attr='elaboration.html')
    postscript = serpy.MethodField()
    cachedImages = serpy.Field(attr='cached_images')
    primaryImage = serpy.Field(attr='primary_image')
    cachedCitations = serpy.Field(attr='cached_citations')
    tagsHtml = serpy.Field(attr='tags_html')

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return 'occurrences.newoccurrence'

    def get_postscript(self, instance):
        """Return the user-facing postscript HTML."""
        return instance.postscript.html if instance.postscript else ''
