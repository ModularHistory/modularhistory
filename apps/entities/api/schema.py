import logging

import graphene

from apps.entities.api.types import EntityType
from apps.entities.models import Entity


class Query(graphene.ObjectType):
    """GraphQL query for all entities."""

    entities = graphene.List(EntityType)
    entity = graphene.Field(EntityType, slug=graphene.String())

    def resolve_entities(self, info, **kwargs):
        return Entity.objects.all()

    def resolve_entity(self, info, slug: str):
        try:
            return Entity.objects.get(slug=slug)
        except Exception as err:
            logging.error(f'{err}')
            return Entity.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
