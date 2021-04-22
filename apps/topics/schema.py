import graphene

import apps.topics.models.schema as topics_schema


class Query(topics_schema.Query, graphene.ObjectType):
    pass


topicsSchema = graphene.Schema(query=Query)
