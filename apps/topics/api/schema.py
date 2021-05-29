from typing import TYPE_CHECKING

import graphene
from django.core.exceptions import ObjectDoesNotExist

from apps.topics.api.types import TopicType
from apps.topics.models.topic import Topic

if TYPE_CHECKING:
    from django.db.models import QuerySet


class Query(graphene.ObjectType):
    """GraphQL query for all topics."""

    topics = graphene.List(TopicType)
    topic = graphene.Field(TopicType, slug=graphene.String())

    @staticmethod
    def resolve_topics(root, info, **kwargs) -> 'QuerySet[Topic]':
        """Return the queryset against which a 'topics' query should be executed."""
        return Topic.objects.all()

    @staticmethod
    def resolve_topic(root, info, slug: str) -> Topic:
        """Return the topic specified by a 'topic' query."""
        try:
            return Topic.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return Topic.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
