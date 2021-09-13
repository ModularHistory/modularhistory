from django.apps import AppConfig

from core.utils.sync import delay


class RedirectsConfig(AppConfig):
    """Config for the redirects app."""

    name = 'apps.redirects'

    # https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready
    def ready(self) -> None:
        """Perform initialization tasks for the redirects app."""
        from .models import Redirect
        from .tasks import write_map

        if Redirect.objects.exists():
            delay(write_map)
        return super().ready()
