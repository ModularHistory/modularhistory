from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def media(url: str) -> str:
    """Modify the URL to use the correct media path, if necessary."""
    if url.startswith(settings.MEDIA_URL):
        return url
    return f'{settings.MEDIA_URL}{url.lstrip("/")}'.replace('/media/media/', '/media/')
