import logging

import graphene

from apps.sources.api.types import SourceType
from apps.sources.models import Source


class Query(graphene.ObjectType):
    """GraphQL query for all sources."""

    sources = graphene.List(SourceType)
    source = graphene.Field(SourceType, slug=graphene.String())

    def resolve_sources(self, info, **kwargs):
        return Source.objects.all()

    def resolve_source(self, info, slug: str):
        try:
            return Source.objects.get(slug=slug)
        except Exception as err:
            logging.error(f'{err}')
            return Source.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
