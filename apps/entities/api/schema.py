from typing import Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql.error import GraphQLError

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
    def resolve_entity(root, info, slug: str) -> Optional[Entity]:
        """Return the entity specified by an 'entity' query."""
        try:
            return Entity.objects.get(slug=slug)
        except ObjectDoesNotExist:
            if slug.isnumeric():
                try:
                    return Entity.objects.get(pk=int(slug))
                except GraphQLError:
                    pass
        return None


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
