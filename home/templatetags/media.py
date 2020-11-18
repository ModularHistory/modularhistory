from django import template

from modularhistory.settings import MEDIA_URL

register = template.Library()


@register.simple_tag
def media(url: str) -> str:
    """Modify the URL to use the correct media path, if necessary."""
    if url.startswith(MEDIA_URL):
        return url
    return f'{MEDIA_URL}{url.lstrip("/")}'.replace('/media/media/', '/media/')
