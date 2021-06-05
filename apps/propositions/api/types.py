from typing import TYPE_CHECKING

import graphene
from graphene.types.generic import GenericScalar

from apps.graph.types import ModuleType
from apps.propositions.models.argument import Argument
from apps.propositions.models.proposition import Proposition

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PropositionArgumentType(ModuleType):
    """GraphQL type for the Proposition model."""

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

    class Meta:
        model = Proposition
        exclude = []

    @staticmethod
    def resolve_arguments(root: Proposition, *args) -> 'QuerySet[Argument]':
        """Return the value to be assigned to a proposition's `model` attribute."""
        return root.arguments.all()

    @staticmethod
    def resolve_model(*args) -> str:
        """Return the value to be assigned to a proposition's `model` attribute."""
        return 'propositions.proposition'
