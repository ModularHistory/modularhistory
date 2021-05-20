from apps.graph.types import ModuleType
from apps.propositions.models.proposition import Proposition


class PropositionType(ModuleType):
    """GraphQL type for the Proposition model."""

    class Meta:
        model = Proposition
        exclude = ['version']

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to a proposition's `model` attribute."""
        return 'propositions.proposition'
