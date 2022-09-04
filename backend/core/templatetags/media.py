import logging
import re

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def media(url: str) -> str:
    """Modify the URL to use the correct media path, if necessary."""
    if url.startswith(settings.MEDIA_URL):
        return url
    try:
        return re.sub(r'.+/media/', '/media/', url)
    except Exception as err:
        logging.error(f'{err}')
        return url
