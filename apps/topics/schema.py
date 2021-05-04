import graphene

from apps.topics.models import schema


class Query(schema.Query, graphene.ObjectType):
    pass


topicsSchema = graphene.Schema(query=Query)
