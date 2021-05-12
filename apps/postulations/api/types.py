from apps.graph.types import ModuleType
from apps.postulations.models.postulation import Postulation


class PostulationType(ModuleType):
    """GraphQL type for the Postulation model."""

    class Meta:
        model = Postulation
        exclude = ['version']

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to a postulation's `model` attribute."""
        return 'postulations.postulation'
