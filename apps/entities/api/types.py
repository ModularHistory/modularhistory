from graphene.types.generic import GenericScalar

from apps.entities.models.entity import Entity
from apps.graph.types import ModuleType


class EntityType(ModuleType):
    """GraphQL type for the Entity model."""

    serialized_images = GenericScalar(source='serialized_images')

    class Meta:
        model = Entity
        exclude = ['type']

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to an entity's `model` attribute."""
        return 'entities.entity'
