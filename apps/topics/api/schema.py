
import graphene
from django.core.exceptions import ObjectDoesNotExist

from apps.topics.api.types import TopicType
from apps.topics.models import Topic


class Query(graphene.ObjectType):
    """GraphQL query for all topics."""

    topics = graphene.List(TopicType)
    topic = graphene.Field(TopicType, slug=graphene.String())

    def resolve_topics(self, info, **kwargs):
        return Topic.objects.all()

    def resolve_topic(self, info, slug: str):
        try:
            return Topic.objects.get(slug=slug)
        except ObjectDoesNotExist:
            return Topic.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
