
import graphene
from graphene_django.types import DjangoObjectType

from apps.entities.models.entity import Entity


class EntityType(DjangoObjectType):
    """GraphQL type for the Entity model."""

    serialized_images = graphene.JSONString(source='serialized_images')

    # required in order to use the ModuleDetail component
    model = graphene.String()

    # required in order to render the admin link
    admin_url = graphene.String(source='admin_url')

    class Meta:
        model = Entity
        exclude = ['type']

    def resolve_model(self, *args) -> str:
        return 'entities.entity'
