import sys

from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.core.checks import Warning, register

from core.constants.environments import Environments
from core.environment import ENVIRONMENT


def superuser_check(app_configs, **kwargs):
    """Check that a superuser has been created."""
    check_for_superuser = (
        ENVIRONMENT == Environments.DEV
        and sys.argv[1] == 'runserver'
        and not get_user_model().objects.filter(is_superuser=True).exists()
    )
    if not check_for_superuser:
        return []
    return [
        Warning(
            'To create a superuser (for testing), run this command: \n\n\t'
            'poetry run python manage.py createsuperuser\n',
        )
    ]


class UsersConfig(AppConfig):
    """Config for the users app."""

    name = 'apps.users'

    def ready(self) -> None:
        """
        Perform initialization tasks for the users app.

        https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready
        """
        ready = super().ready()
        register(superuser_check)
        return ready
