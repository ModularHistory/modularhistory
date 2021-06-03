from typing import TYPE_CHECKING

import graphene

from apps.graph.types import ModuleType
from apps.propositions.api.types import PropositionType
from apps.topics.models.topic import Topic

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.propositions.models.proposition import PolymorphicProposition


class TopicType(ModuleType):
    """GraphQL type for the Topic model."""

    propositions = graphene.List(PropositionType)

    class Meta:
        model = Topic
        exclude = []

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to a topic's `model` attribute."""
        return 'topics.topic'

    @staticmethod
    def resolve_propositions(root: Topic, *args) -> 'QuerySet[PolymorphicProposition]':
        """Return the value to be assigned to a proposition's `model` attribute."""
        return root.polymorphicproposition_set.all()
