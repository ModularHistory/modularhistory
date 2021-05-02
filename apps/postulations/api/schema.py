import logging

import graphene

from apps.postulations.api.types import PostulationType
from apps.postulations.models import Postulation


class Query(graphene.ObjectType):
    """GraphQL query for all postulations."""

    postulations = graphene.List(PostulationType)
    postulation = graphene.Field(PostulationType, slug=graphene.String())

    def resolve_postulations(self, info, **kwargs):
        return Postulation.objects.all()

    def resolve_postulation(self, info, slug: str):
        try:
            return Postulation.objects.get(slug=slug)
        except Exception as err:
            logging.error(f'{err}')
            return Postulation.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
