from django.apps import AppConfig

from core.utils.sync import delay


class RedirectsConfig(AppConfig):
    """Config for the redirects app."""

    name = 'apps.redirects'

    # https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready
    def ready(self) -> None:
        """Perform initialization tasks for the redirects app."""
        from .tasks import write_map

        delay(write_map)
        return super().ready()
