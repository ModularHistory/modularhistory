from django.apps import AppConfig


class EntitiesConfig(AppConfig):
    """Config for the entities app."""

    name = 'apps.entities'

    def ready(self) -> None:
        """Perform initialization tasks for the entities app."""
        from . import signals  # noqa: F401

        return super().ready()
