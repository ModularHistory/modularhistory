"""Serializers for the entities app."""

import serpy

from modularhistory.models.model import ModelSerializer


class TopicSerializer(ModelSerializer):
    """Serializer for topics."""

    key = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of serialized topics."""
        return 'topics.topic'
