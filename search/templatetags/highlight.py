from django import template
from django.utils.safestring import mark_safe
from haystack.utils.highlighting import Highlighter

register = template.Library()


@register.filter(is_safe=True)
def highlight(value: str, text: str = ''):
    html = value
    highlighter = Highlighter(text)
    return mark_safe(highlighter.highlight(html))
