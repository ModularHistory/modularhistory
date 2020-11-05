from django import template
from modularhistory.settings import MEDIA_URL
from urllib.parse import urljoin

register = template.Library()


@register.simple_tag
def media(url: str) -> str:
    if url.startswith(MEDIA_URL):
        return url
    return urljoin(MEDIA_URL, url).replace('/media/media/', '/media/')
