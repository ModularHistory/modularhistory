import graphene
from graphene_django.types import DjangoObjectType

from apps.topics.models.topic import Topic


# GraphQL type for Topic model
class TopicType(DjangoObjectType):
    pk = graphene.Int(source='pk')  # adding private key to the fields

    class Meta:
        model = Topic
        fields = (
            'name',
            'pk',
        )
