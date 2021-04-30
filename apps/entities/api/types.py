import graphene
from graphene_django.types import DjangoObjectType

from apps.entities.models.entity import Entity


# GraphQL type for Entity model
class EntityType(DjangoObjectType):
    """GraphQL type for entities."""

    serialized_images = graphene.JSONString(source='serialized_images')

    class Meta:
        model = Entity
        exclude = ['type']
