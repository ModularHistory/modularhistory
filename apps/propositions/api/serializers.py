from core.models.model import ModelSerializer


class PropositionSerializer(ModelSerializer):
    """Serializer for propositions."""

    def get_model(self, instance) -> str:  # noqa
        """Return the model name of serialized propositions."""
        return 'propositions.proposition'
