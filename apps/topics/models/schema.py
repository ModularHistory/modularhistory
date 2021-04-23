import graphene
from graphene_django.types import DjangoObjectType, ObjectType

from apps.topics.models.topic import Topic


# GraphQL type for Topic model
class TopicType(DjangoObjectType):
    pk = graphene.Int(source='pk')  # adding private key to the fields

    class Meta:
        model = Topic
        fields = (
            'key',
            'pk',
        )


# GraphQL query for all Topics with the fields of 'key' and 'pk'
class Query(graphene.ObjectType):
    all_topics = graphene.List(TopicType)

    def resolve_all_topics(self, info, **kwargs):
        return Topic.objects.all()


schema = graphene.Schema(query=Query)


def query_result():
    result = schema.execute(
        '''
        query {
          allTopics {
            key
            pk
        }
    }'''
    )
    return result.data['allTopics']
