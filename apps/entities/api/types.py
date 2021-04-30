import graphene

from apps.entities.models.entity import Entity
from apps.graph.types import ModuleType


class EntityType(ModuleType):
    """GraphQL type for the Entity model."""

    serialized_images = graphene.JSONString(source='serialized_images')

    class Meta:
        model = Entity
        exclude = ['type']

    def resolve_model(self, *args) -> str:
        return 'entities.entity'
