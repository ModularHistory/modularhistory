import logging

import graphene

from apps.postulations.api.types import PostulationType
from apps.postulations.models import Postulation


class Query(graphene.ObjectType):
    """GraphQL query for all postulations."""

    postulations = graphene.List(PostulationType)
    postulation = graphene.Field(PostulationType, slug=graphene.String())

    @staticmethod
    def resolve_postulations(root, info, **kwargs):
        """Return the queryset against which a 'postulations' query should be executed."""
        return Postulation.objects.all()

    @staticmethod
    def resolve_postulation(root, info, slug: str):
        """Return the postulation specified by a 'postulation' query."""
        try:
            return Postulation.objects.get(slug=slug)
        except Exception as err:
            logging.error(f'{err}')
            return Postulation.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
