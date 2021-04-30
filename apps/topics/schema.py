import graphene

from apps.topics.models import Topic
from apps.topics.types import TopicType


class Query(graphene.ObjectType):
    """GraphQL query for all topics."""

    topics = graphene.List(TopicType)

    def resolve_topics(self, info, **kwargs):
        return Topic.objects.all()


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
