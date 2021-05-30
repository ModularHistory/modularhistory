from typing import TYPE_CHECKING

import graphene
from django.core.exceptions import ObjectDoesNotExist

from apps.propositions.api.types import PropositionType
from apps.propositions.models import PolymorphicProposition

if TYPE_CHECKING:
    from django.db.models import QuerySet


class Query(graphene.ObjectType):
    """GraphQL query for all propositions."""

    propositions = graphene.List(PropositionType)
    proposition = graphene.Field(PropositionType, slug=graphene.String())

    @staticmethod
    def resolve_propositions(*args, **kwargs) -> 'QuerySet[PolymorphicProposition]':
        """Return the queryset against which a 'propositions' query should be executed."""
        return PolymorphicProposition.objects.all()

    @staticmethod
    def resolve_proposition(*args, slug: str) -> PolymorphicProposition:
        """Return the proposition specified by a 'proposition' query."""
        try:
            return PolymorphicProposition.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return PolymorphicProposition.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
