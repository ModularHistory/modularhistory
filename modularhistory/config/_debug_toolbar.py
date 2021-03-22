"""
Post-settings config for the Django Debug Toolbar.

NOTE: As modularhistory.settings is accessed in this module,
the settings/logic in this module must be accessed AFTER
modularhistory.settings is loaded.

Config reference:
https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html
"""
from django.conf import settings
from django.http import HttpRequest


def show_toolbar(request: HttpRequest) -> bool:
    """Determine whether to display the debug toolbar."""
    conditions = (
        settings.DEBUG and request.META.get('REMOTE_ADDR', None) in settings.INTERNAL_IPS,
        request.user.is_superuser,
    )
    disqualifiers = (
        [settings.TESTING]
    )
    if any(conditions) and not any(disqualifiers):
        return True
    return False
