from typing import TYPE_CHECKING

import graphene
from graphene.types.generic import GenericScalar

from apps.cms.api.types import PullRequestType
from apps.graph.types import ModuleType
from apps.propositions.models.argument import Argument
from apps.propositions.models.proposition import Proposition

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PropositionArgumentType(ModuleType):
    """GraphQL type for the Proposition model."""

    pk = graphene.String()

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
    pull_requests = graphene.List(PullRequestType)
    cached_images = GenericScalar(source='cached_images')

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
    def resolve_pull_requests(root: Proposition, *args) -> 'QuerySet[Argument]':  # noqa: D102
        return root.pull_requests.all()

    @staticmethod
    def resolve_model(*args) -> str:  # noqa: D102
        return 'propositions.proposition'
