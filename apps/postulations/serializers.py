"""Serializers for the entities app."""

import serpy

from modularhistory.models.model import ModelSerializer


class PostulationSerializer(ModelSerializer):
    """Serializer for postulations."""

    summary = serpy.MethodField()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the postulation."""
        return 'postulations.postulation'

    def get_summary(self, instance) -> str:  # noqa
        """Return the model name of the postulation."""
        return instance.summary.html
