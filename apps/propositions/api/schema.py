
import graphene
from django.core.exceptions import ObjectDoesNotExist

from apps.propositions.api.types import PropositionType
from apps.propositions.models import TypedProposition


class Query(graphene.ObjectType):
    """GraphQL query for all propositions."""

    propositions = graphene.List(PropositionType)
    proposition = graphene.Field(PropositionType, slug=graphene.String())

    @staticmethod
    def resolve_propositions(root, info, **kwargs):
        """Return the queryset against which a 'propositions' query should be executed."""
        return TypedProposition.objects.all()

    @staticmethod
    def resolve_proposition(root, info, slug: str):
        """Return the proposition specified by a 'proposition' query."""
        try:
            return TypedProposition.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return TypedProposition.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)