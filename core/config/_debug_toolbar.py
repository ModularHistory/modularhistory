"""
Post-settings config for the Django Debug Toolbar.

NOTE: As core.settings is accessed in this module,
the settings/logic in this module must be accessed AFTER
core.settings is loaded.

Config reference:
https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html
"""
from django.conf import settings
from django.http import HttpRequest


def show_toolbar(request: HttpRequest) -> bool:
    """Determine whether to display the debug toolbar."""
    qualifiers = (
        settings.DEBUG
        and request.META.get('REMOTE_ADDR', None) in settings.INTERNAL_IPS,
        request.user.is_superuser,
    )
    disqualifiers = (
        settings.TESTING,
        '/api/' in request.path,
        request.path == '/healthcheck/',
    )
    if any(qualifiers) and not any(disqualifiers):
        return True
    return False
