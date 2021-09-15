from django.apps import AppConfig


class QuotesConfig(AppConfig):
    """Config for the quotes app."""

    name = 'apps.quotes'

    def ready(self) -> None:
        """Perform initialization tasks for the quotes app."""
        from . import signals  # noqa: F401

        return super().ready()
