"""Serializers for the stories app."""

import serpy

from apps.search.api.serializers import SearchableModelSerializer


class StorySerializer(SearchableModelSerializer):
    """Serializer for occurrences."""

    handle = serpy.Field()
    description = serpy.MethodField()
    cachedCitations = serpy.Field(attr='cached_citations')

    def get_model(self, instance) -> str:
        """Return the model name of the instance."""
        return 'stories.story'

    def get_description(self, instance) -> str:
        """Return the user-facing description HTML."""
        html = instance.description.html if instance.description else ''
        return html
