import graphene
from graphene_django.types import DjangoObjectType

from apps.topics.models import Topic
from apps.topics.types import TopicType


# GraphQL query for all Topics with the fields of 'name' and 'pk'
class Query(graphene.ObjectType):
    all_topics = graphene.List(TopicType)

    def resolve_all_topics(self, info, **kwargs):
        return Topic.objects.all()


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
