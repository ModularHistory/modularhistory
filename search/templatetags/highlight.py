from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def highlight(value: str, text: str = ''):
    html = value
    for word in text.split(' '):
        html = html.replace(
            word,
            f'<span class="highlighted">{word}</span>'
        )
    return mark_safe(html)
