from typing import TYPE_CHECKING, Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphene.types.generic import GenericScalar
from graphql.error import GraphQLError
from titlecase import titlecase

from apps.graph.types import ModuleType
from apps.propositions.models import Proposition
from apps.propositions.models.argument import Argument

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PropositionArgumentType(ModuleType):
    """GraphQL type for the Proposition model."""

    pk = graphene.Int()

    class Meta:
        model = Argument
        exclude = []

    @staticmethod
    def resolve_model(*args) -> str:
        """Return the value to be assigned to an argument's `model` attribute."""
        return 'propositions.argument'


class PropositionType(ModuleType):
    """GraphQL type for the Proposition model."""

    arguments = graphene.List(PropositionArgumentType)
    cached_images = GenericScalar(source='cached_images')
    title = graphene.String()

    class Meta:
        model = Proposition
        # https://docs.graphene-python.org/projects/django/en/latest/queries/#choices-to-enum-conversion
        convert_choices_to_enum = False
        # https://github.com/graphql-python/graphene-django/issues/185
        exclude = ['type']

    @staticmethod
    def resolve_arguments(root: Proposition, *args) -> 'QuerySet[Argument]':  # noqa: D102
        return root.arguments.all()

    @staticmethod
    def resolve_model(*args) -> str:  # noqa: D102
        return 'propositions.proposition'

    @staticmethod
    def resolve_title(root: Proposition, *args) -> str:
        return titlecase(root.title)


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
                except GraphQLError:
                    pass
        return None


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
