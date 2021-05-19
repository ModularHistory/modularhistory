import logging

import graphene

from apps.sources.api.types import SourceType
from apps.sources.models.source import Source


class Query(graphene.ObjectType):
    """GraphQL query for all sources."""

    sources = graphene.List(SourceType)
    source = graphene.Field(SourceType, slug=graphene.String())

    @staticmethod
    def resolve_sources(root, info, **kwargs):
        """Return the queryset against which a 'sources' query should be executed."""
        return Source.objects.all()

    @staticmethod
    def resolve_source(root, info, slug: str):
        """Return the source specified by a 'source' query."""
        try:
            return Source.objects.get(slug=slug)
        except Exception as err:
            logging.error(f'{err}')
            return Source.objects.get(pk=slug)


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
