from sentry_sdk import capture_exception

from core.environment import IS_DEV


class SentryMiddleware:
    """GraphQL middleware for error handling."""

    def on_error(self, error):
        """
        Properly capture errors during query execution and send them to Sentry.
        Then raise the error again and let Graphene handle it.
        """
        if not IS_DEV:
            capture_exception(error)
        raise error

    def resolve(self, next, root, info, **args):
        return next(root, info, **args).catch(self.on_error)
