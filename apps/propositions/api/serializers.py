import serpy

from core.models.model import ModelSerializer


class PropositionSerializer(ModelSerializer):
    """Serializer for propositions."""

    slug = serpy.StrField()
    summary = serpy.MethodField()
    elaboration = serpy.StrField()

    def get_summary(self, instance) -> str:
        """Return the model name of the postulation."""
        return instance.summary.html

    def get_model(self, instance) -> str:
        """Return the model name of serialized propositions."""
        return 'propositions.proposition'
