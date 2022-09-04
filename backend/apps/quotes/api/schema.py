from typing import Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from graphene.types.generic import GenericScalar
from graphql.error import GraphQLError

from apps.graph.types import ModuleType
from apps.quotes.models.quote import Quote


class QuoteType(ModuleType):
    """GraphQL type for the Quote model."""

    cached_images = GenericScalar(source='cached_images')

    class Meta:
        model = Quote
        # https://github.com/graphql-python/graphene-django/issues/185
        exclude = ['type']

    @staticmethod
    def resolve_model(root: Quote, *args) -> str:
        """Return the value to be assigned to an quote's `model` attribute."""
        return 'quotes.quote'


class Query(graphene.ObjectType):
    """GraphQL query for all quotes."""

    quotes = graphene.List(QuoteType, ids=graphene.List(graphene.Int))
    quote = graphene.Field(QuoteType, slug=graphene.String())

    @staticmethod
    def resolve_quotes(root, info, ids: list[int], **kwargs):
        """Return the queryset against which an 'quotes' query should be executed."""
        return Quote.objects.filter(id__in=ids)

    @staticmethod
    def resolve_quote(root, info, slug: str) -> Optional[Quote]:
        """Return the quote specified by an 'quote' query."""
        try:
            return Quote.objects.get(slug=slug)
        except ObjectDoesNotExist:
            if slug.isnumeric():
                try:
                    return Quote.objects.get(pk=int(slug))
                except GraphQLError:
                    pass
        return None


# class Mutation(graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
