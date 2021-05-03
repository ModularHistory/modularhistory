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

    def resolve_model(self, *args):
        return 'sources.source'
