"""Serializers for the postulations app."""

import serpy

from core.models.model import ModelSerializer


class PostulationSerializer(ModelSerializer):
    """Serializer for postulations."""

    summary = serpy.MethodField()

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of the postulation."""
        return 'postulations.postulation'

    def get_summary(self, instance) -> str:  # noqa
        """Return the model name of the postulation."""
        return instance.summary.html
