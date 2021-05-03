
import graphene

from apps.entities.api.types import EntityType
from apps.entities.models import Entity


class Query(graphene.ObjectType):
    """GraphQL query for all entities."""

    entities = graphene.List(EntityType)
    entity = graphene.Field(EntityType, slug=graphene.String())

    @staticmethod
    def resolve_entities(root, info, **kwargs):
        return Entity.objects.all()

    @staticmethod
    def resolve_entity(root, info, slug: str):
        return Entity.objects.get(slug=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
