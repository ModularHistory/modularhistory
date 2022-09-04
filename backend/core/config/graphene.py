from sentry_sdk.integrations.logging import ignore_logger

from core.environment import IS_DEV

ignore_logger('graphql.execution.utils')


GRAPHENE = {
    'SCHEMA': 'apps.graph.schema.schema',
    # 'MIDDLEWARE': (
    #     'graphene_django.debug.DjangoDebugMiddleware',
    #     'core.config._graphene.SentryMiddleware',
    # ),
}
if IS_DEV:
    GRAPHENE['MIDDLEWARE'] = ('graphene_django.debug.DjangoDebugMiddleware',)
