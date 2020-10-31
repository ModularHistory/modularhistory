from django import template
from modularhistory.settings import MEDIA_URL

register = template.Library()


@register.simple_tag
def media(url: str) -> str:
    if url.startswith(MEDIA_URL):
        return url
    url = url.lstrip('/media/')
    return f'{MEDIA_URL}/{url}'
