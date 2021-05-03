import graphene

from apps.graph.types import AbstractModuleType
from apps.sources.models import Source


class SourceType(AbstractModuleType):
    """GraphQL type for the Source model."""

    slug = graphene.String()
    citation_html = graphene.String()
    citation_string = graphene.String()
    attributee_html = graphene.String()
    title = graphene.String()

    @classmethod
    def resolve_model(cls, instance: Source, info):
        return 'sources.source'
