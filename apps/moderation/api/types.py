import graphene
from graphene_django.types import DjangoObjectType

from apps.moderation.models.change import Change


class ChangeType(DjangoObjectType):
    """GraphQL type for the Change model."""

    id = graphene.Int()

    class Meta:
        model = Change
        exclude = []
