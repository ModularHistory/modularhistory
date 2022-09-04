"""
This GraphQL schema unifies the schemas defined in other apps.

To allow another model to be queried/mutated, update the Query and/or Mutation
classes in this module.
"""

import graphene
from graphene_django.debug import DjangoDebug

from apps.entities.api import schema as entities_schema
from apps.images.api import schema as images_schema
from apps.propositions.api import schema as propositions_schema
from apps.quotes.api import schema as quotes_schema
from apps.sources.api import schema as sources_schema
from apps.topics.api import schema as topics_schema


class Query(
    entities_schema.Query,
    images_schema.Query,
    propositions_schema.Query,
    sources_schema.Query,
    topics_schema.Query,
    quotes_schema.Query,
):
    """
    Unified GraphQL query.

    To output SQL while testing GraphQL requests, use the following to the query:
    ``
        exampleQuery {
            exampleFieldOne
            exampleFieldTwo
        }
        _debug {
            sql {
            rawSql
            }
        }
    ``
    """

    # Enable outputting SQL queries (for testing/debugging).
    debug = graphene.Field(DjangoDebug, name='_debug')


# class Mutation(topics_schema.Mutation, graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
