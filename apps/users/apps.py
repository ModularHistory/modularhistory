from django.apps import AppConfig
from django.core.checks import Warning, register


def superuser_check(app_configs, **kwargs):
    """Check that a superuser has been created."""
    from apps.users.models import User

    if User.objects.filter(is_superuser=True).exists():
        return []
    return [
        Warning(
            'You need to create a superuser. To do so, run this command: \n\n\t'
            'poetry run python manage.py createsuperuser \n',
        )
    ]


class AccountConfig(AppConfig):
    """Config for the users app."""

    name = 'apps.users'

    def ready(self) -> None:
        """
        Perform initialization tasks for the users app.

        https://docs.djangoproject.com/en/3.1/ref/applications/#django.apps.AppConfig.ready
        """
        ready = super().ready()
        register(superuser_check)
        return ready
