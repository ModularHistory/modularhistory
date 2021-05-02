import graphene

from apps.graph.types import ModuleType
from apps.postulations.models.postulation import Postulation


class PostulationType(ModuleType):
    """GraphQL type for the Postulation model."""

    class Meta:
        model = Postulation
        exclude = []

    def resolve_model(self, *args) -> str:
        return 'postulations.postulation'
