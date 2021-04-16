import sys

from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.core.checks import Warning, register

from core.constants.environments import Environments
from core.environment import ENVIRONMENT


def superuser_check(app_configs, **kwargs):
    """Check that a superuser has been created."""
    conditions = [
        ENVIRONMENT == Environments.DEV,
        sys.argv[1] == 'runserver',
        not get_user_model().objects.filter(is_superuser=True).exists(),
    ]
    if not all(conditions):
        return []
    return [
        Warning(
            'To create a superuser (for testing), run this command: \n\n\t'
            f'poetry run python manage.py createsuperuser\n',
        )
    ]


class UsersConfig(AppConfig):
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
