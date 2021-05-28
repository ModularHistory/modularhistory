from sentry_sdk import capture_exception

from core.environment import IS_DEV

# https://docs.graphene-python.org/en/latest/execution/middleware/


class SentryMiddleware:
    """GraphQL middleware for error handling."""

    def on_error(self, error):
        """Handle errors raised during query execution."""
        if not IS_DEV:
            # Properly capture the error and send it to Sentry.
            capture_exception(error)
        # Raise the error again and let Graphene handle it.
        raise error

    def resolve(self, next, root, info, **args):
        """Continue evaluation by returning the next middleware."""
        return next(root, info, **args).catch(self.on_error)
