from django.apps import AppConfig


class PropositionsConfig(AppConfig):
    """Config for the propositions app."""

    name = 'apps.propositions'

    def ready(self) -> None:
        """Perform initialization tasks for the propositions app."""
        from . import signals  # noqa: F401

        return super().ready()
