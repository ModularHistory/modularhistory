import graphene

from apps.graph.types import ModuleType
from apps.postulations.models.postulation import Postulation


class PostulationType(ModuleType):
    """GraphQL type for the Postulation model."""

    class Meta:
        model = Postulation
        exclude = []

    @staticmethod
    def resolve_model(root, *args) -> str:
        return 'postulations.postulation'
