"""Serializers for the entities app."""

from modularhistory.models.model import ModelSerializer
import serpy


class TopicSerializer(ModelSerializer):
    """Serializer for topics."""

    key = serpy.Field()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the instance."""
        return f'topics.topic'
