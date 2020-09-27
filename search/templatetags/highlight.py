from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter(is_safe=True)
def highlight(value: str, text: str = ''):
    """TODO: add docstring."""
    html = value
    for word in text.split(' '):
        html = html.replace(
            word,
            f'<span class="highlighted">{word}</span>'
        )
    return format_html(html)
