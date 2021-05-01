import graphene

from apps.entities.api import schema as entities_schema
from apps.sources.api import schema as sources_schema
from apps.topics.api import schema as topics_schema


# add other queries to the parameters of the following query to make additions:
class Query(entities_schema.Query, sources_schema.Query, topics_schema.Query):
    pass


# class Mutation(topics_schema.Mutation, graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
