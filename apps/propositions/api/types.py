from apps.graph.types import ModuleType
from apps.propositions.models.proposition import TypedProposition


class PropositionType(ModuleType):
    """GraphQL type for the TypedProposition model."""

    class Meta:
        model = TypedProposition
        exclude = ['version']

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to a proposition's `model` attribute."""
        return 'propositions.proposition'
