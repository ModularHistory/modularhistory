from typing import Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphene.types.generic import GenericScalar
from graphql.error import GraphQLError

from apps.entities.models.entity import Entity
from apps.graph.types import ModuleType
from apps.quotes.api.schema import QuoteType


class EntityType(ModuleType):
    """GraphQL type for the Entity model."""

    cached_images = GenericScalar(source='cached_images')
    related_quotes = graphene.List(QuoteType, slug=graphene.String())

    class Meta:
        model = Entity
        # https://github.com/graphql-python/graphene-django/issues/185
        exclude = ['type']

    @staticmethod
    def resolve_model(root: Entity, *args) -> str:
        """Return the value to be assigned to an entity's `model` attribute."""
        return 'entities.entity'

    @staticmethod
    def resolve_related_quotes(root: Entity, *args, **kwargs):
        return root.quotes.all()


class Query(graphene.ObjectType):
    """GraphQL query for all entities."""

    entities = graphene.List(EntityType, ids=graphene.List(graphene.Int))
    entity = graphene.Field(EntityType, slug=graphene.String())

    @staticmethod
    def resolve_entities(root, info, ids: list[int], **kwargs):
        """Return the queryset against which an 'entities' query should be executed."""
        return Entity.objects.filter(id__in=ids)

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
