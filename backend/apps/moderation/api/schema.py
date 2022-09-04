from typing import Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphene_django.types import DjangoObjectType

from apps.entities.models.entity import Entity
from apps.moderation.models.change import Change


class ChangeType(DjangoObjectType):
    """GraphQL type for the Change model."""

    pk = graphene.Int()

    class Meta:
        model = Change
        exclude = []


class Query(graphene.ObjectType):
    """GraphQL query for changes."""

    changes = graphene.List(ChangeType)
    change = graphene.Field(ChangeType, id=graphene.Int())

    @staticmethod
    def resolve_changes(root, info, **kwargs):
        """Return the queryset against which a 'changes' query should be executed."""
        return Change.objects.all()

    @staticmethod
    def resolve_change(root, info, id: int) -> Optional[Entity]:
        """Return the change specified by a 'change' query."""
        try:
            return Change.objects.get(id=id)
        except ObjectDoesNotExist:
            return None


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
