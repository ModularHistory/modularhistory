from graphene_django.types import DjangoObjectType

from apps.cms.models import PullRequest


class PullRequestType(DjangoObjectType):
    """GraphQL type for the PullRequest model."""

    class Meta:
        model = PullRequest
        exclude = []
