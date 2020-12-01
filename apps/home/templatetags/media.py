from django import template

from django.conf import settings
from modularhistory.constants.misc import Environments

register = template.Library()


@register.simple_tag
def media(url: str) -> str:
    """Modify the URL to use the correct media path, if necessary."""
    if url.startswith(settings.MEDIA_URL):
        return url
    elif settings.ENVIRONMENT == Environments.DEV:
        return url.replace(
            settings.MEDIA_URLS.get(Environments.PROD),
            settings.MEDIA_URLS.get(Environments.DEV),
        )
    return f'{settings.MEDIA_URL}{url.lstrip("/")}'.replace('/media/media/', '/media/')
