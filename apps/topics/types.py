import graphene
from graphene_django.types import DjangoObjectType

from apps.topics.models.topic import Topic


# GraphQL type for Topic model
class TopicType(DjangoObjectType):
    """GraphQL type for topics."""

    # Add primary key to the fields.
    pk = graphene.Int(source='pk')

    class Meta:
        model = Topic
        exclude = ['related']
        # fields = (
        #     'name',
        #     'pk',
        # )
