from graphene.types.generic import GenericScalar

from apps.entities.models.entity import Entity
from apps.graph.types import ModuleType


class EntityType(ModuleType):
    """GraphQL type for the Entity model."""

    cached_images = GenericScalar(source='cached_images')

    class Meta:
        model = Entity
        # https://github.com/graphql-python/graphene-django/issues/185
        exclude = ['type']

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to an entity's `model` attribute."""
        return 'entities.entity'
