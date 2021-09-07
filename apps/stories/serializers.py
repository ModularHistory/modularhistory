"""Serializers for the stories app."""

import serpy

from core.models.module import ModuleSerializer


class StorySerializer(ModuleSerializer):
    """Serializer for occurrences."""

    handle = serpy.Field()
    description = serpy.StrField()
    cached_citations = serpy.Field()

    def get_model(self, instance) -> str:
        """Return the model name of the instance."""
        return 'stories.story'
