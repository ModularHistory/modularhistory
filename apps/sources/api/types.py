import graphene

from apps.graph.types import AbstractModuleType


class SourceType(AbstractModuleType):
    """GraphQL type for the Source model."""

    slug = graphene.String()
    citation_html = graphene.String()
    citation_string = graphene.String()
    attributee_html = graphene.String()
    title = graphene.String()

    @staticmethod
    def resolve_model(root, *args):
        return 'sources.source'
