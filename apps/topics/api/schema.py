from typing import TYPE_CHECKING, Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphql.error.located_error import GraphQLLocatedError

from apps.topics.api.types import TopicType
from apps.topics.models.topic import Topic

if TYPE_CHECKING:
    from django.db.models import QuerySet


class Query(graphene.ObjectType):
    """GraphQL query for all topics."""

    topics = graphene.List(TopicType)
    topics_with_conclusions = graphene.List(TopicType)
    topic = graphene.Field(TopicType, slug=graphene.String())

    @staticmethod
    def resolve_topics(root, info, **kwargs) -> 'QuerySet[Topic]':
        """Return the queryset against which a 'topics' query should be executed."""
        return Topic.objects.all()

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
                except GraphQLLocatedError:
                    pass
        return None


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
