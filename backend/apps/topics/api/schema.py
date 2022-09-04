from typing import TYPE_CHECKING, Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql.error import GraphQLError

from apps.graph.types import ModuleType
from apps.propositions.api.schema import PropositionType
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


class Query(graphene.ObjectType):
    """GraphQL query for all topics."""

    topics = graphene.List(TopicType, ids=graphene.List(graphene.Int))
    topics_with_conclusions = graphene.List(TopicType)
    topic = graphene.Field(TopicType, slug=graphene.String())

    @staticmethod
    def resolve_topics(root, info, ids: list[int], **kwargs) -> 'QuerySet[Topic]':
        """Return the queryset against which a 'topics' query should be executed."""
        queryset = Topic.objects.all()
        if ids:
            queryset = queryset.filter(id__in=ids)
        return queryset

    @staticmethod
    def resolve_topics_with_conclusions(root, info, **kwargs) -> 'QuerySet[Topic]':
        """Return the queryset against which a 'topics' query should be executed."""
        return Topic.objects.filter(
            proposition_set__type='propositions.conclusion'
        ).distinct()

    @staticmethod
    def resolve_topic(root, info, slug: str) -> Optional[Topic]:
        """Return the topic specified by a 'topic' query."""
        try:
            return Topic.objects.get(slug=slug)
        except ObjectDoesNotExist:
            if slug.isnumeric():
                try:
                    return Topic.objects.get(pk=int(slug))
                except GraphQLError:
                    pass
        return None


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
