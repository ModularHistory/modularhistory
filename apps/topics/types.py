import graphene
from graphene_django.types import DjangoObjectType

from apps.topics.models.topic import Topic


class TopicType(DjangoObjectType):
    """GraphQL type for the Topic model."""

    # Add primary key to the fields.
    pk = graphene.Int(source='pk')

    class Meta:
        model = Topic
        exclude = ['related']
