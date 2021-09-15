from django.apps import AppConfig


class QuotesConfig(AppConfig):
    """Config for the quotes app."""

    name = 'apps.quotes'

    # https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready
    def ready(self) -> None:
        """Perform initialization tasks for the sources app."""
        # Since our signal receivers use the receiver() decorator,
        # we must import the signals submodule inside ready().
        # https://docs.djangoproject.com/en/dev/topics/signals/#connecting-receiver-functions
        from . import signals  # noqa: F401

        return super().ready()
