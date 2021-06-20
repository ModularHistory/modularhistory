from typing import TYPE_CHECKING

import graphene
from graphene import relay

from apps.graph.types import ModuleType
from apps.propositions.api.types import PropositionType
from apps.topics.models.topic import Topic

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.propositions.models.proposition import Proposition


class TopicType(ModuleType):
    """GraphQL type for the Topic model."""

    propositions = graphene.List(PropositionType)
    conclusions = graphene.List(PropositionType)
    occurrences = graphene.List(PropositionType)

    class Meta:
        model = Topic
        filter_fields = []
        exclude = []
        interfaces = (relay.Node,)

    @staticmethod
    def resolve_model(root, *args) -> str:
        """Return the value to be assigned to a topic's `model` attribute."""
        return 'topics.topic'

    @staticmethod
    def resolve_propositions(root: Topic, *args) -> 'QuerySet[Proposition]':
        """Return the topic's propositions."""
        return root.proposition_set.all()

    @staticmethod
    def resolve_conclusions(root: Topic, *args) -> 'QuerySet[Proposition]':
        """Return the topic's conclusions."""
        return root.proposition_set.filter(type='propositions.conclusion')

    @staticmethod
    def resolve_occurrences(root: Topic, *args) -> 'QuerySet[Proposition]':
        """Return the topic's occurrences."""
        return root.proposition_set.filter(type='propositions.occurrence')
