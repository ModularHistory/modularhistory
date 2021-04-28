import graphene

import apps.topics.schema


# add other queries to the parameters of the following query to make additions:
class Query(apps.topics.schema.Query, graphene.ObjectType):
    pass


# class Mutation(apps.topics.schema.Mutation, graphene.ObjectType):
#    pass


# add mutation=Mutation to parameters when adding the first mutation
schema = graphene.Schema(query=Query)
