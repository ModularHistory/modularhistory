import graphene
from graphene_django.types import DjangoObjectType, ObjectType

from apps.topics.models.topic import Topic


# GraphQL type for Topic model
class TopicType(DjangoObjectType):
    class Meta:
        model = Topic


# GraphQL query for all Topics
class Query(object):
    all_topics = graphene.List(TopicType)

    def resolve_all_topics(self, info, **kwargs):
        return Topic.objects.all()
