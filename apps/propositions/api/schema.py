from typing import TYPE_CHECKING, Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql.error.located_error import GraphQLLocatedError

from apps.propositions.api.types import PropositionType
from apps.propositions.models import Proposition

if TYPE_CHECKING:
    from django.db.models import QuerySet


class Query(graphene.ObjectType):
    """GraphQL query for all propositions."""

    propositions = graphene.List(PropositionType)
    proposition = graphene.Field(PropositionType, slug=graphene.String())

    @staticmethod
    def resolve_propositions(*args, **kwargs) -> 'QuerySet[Proposition]':
        """Return the queryset against which a 'propositions' query should be executed."""
        return Proposition.objects.all()

    @staticmethod
    def resolve_proposition(*args, slug: str) -> Optional[Proposition]:
        """Return the proposition specified by a 'proposition' query."""
        try:
            return Proposition.objects.get(slug=slug)
        except ObjectDoesNotExist:
            if slug.isnumeric():
                try:
                    return Proposition.objects.get(pk=int(slug))
                except GraphQLLocatedError:
                    pass
        return None


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
