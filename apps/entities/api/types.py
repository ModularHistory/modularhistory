import graphene

from apps.entities.models.entity import Entity
from apps.graph.types import ModuleType


class EntityType(ModuleType):
    """GraphQL type for the Entity model."""

    serialized_images = graphene.JSONString(source='serialized_images')

    class Meta:
        model = Entity
        exclude = ['type']

    @staticmethod
    def resolve_model(root, *args) -> str:
        return 'entities.entity'
