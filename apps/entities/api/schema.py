import graphene
from django.core.exceptions import ObjectDoesNotExist

from apps.entities.api.types import EntityType
from apps.entities.models.entity import Entity


class Query(graphene.ObjectType):
    """GraphQL query for all entities."""

    entities = graphene.List(EntityType)
    entity = graphene.Field(EntityType, slug=graphene.String())

    @staticmethod
    def resolve_entities(root, info, **kwargs):
        """Return the queryset against which an 'entities' query should be executed."""
        return Entity.objects.all()

    @staticmethod
    def resolve_entity(root, info, slug: str):
        """Return the entity specified by an 'entity' query."""
        try:
            return Entity.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return Entity.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
