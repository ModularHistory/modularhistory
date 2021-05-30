from apps.graph.types import ModuleType
from apps.propositions.models.proposition import PolymorphicProposition


class PropositionType(ModuleType):
    """GraphQL type for the PolymorphicProposition model."""

    class Meta:
        model = PolymorphicProposition
        exclude = []

    @staticmethod
    def resolve_model(*args) -> str:
        """Return the value to be assigned to a proposition's `model` attribute."""
        return 'propositions.proposition'
