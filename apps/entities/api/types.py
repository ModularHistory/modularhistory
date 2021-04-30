import graphene
from graphene_django.types import DjangoObjectType

from apps.entities.models.entity import Entity


class EntityType(DjangoObjectType):
    """GraphQL type for the Entity model."""

    serialized_images = graphene.JSONString(source='serialized_images')

    class Meta:
        model = Entity
        exclude = ['type']
