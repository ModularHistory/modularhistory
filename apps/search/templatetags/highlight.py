from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter(is_safe=True)
def highlight(text_body: str, text_to_highlight: str = ''):
    """Within the text body, highlight instances of the text to highlight."""
    html = text_body
    for word in text_to_highlight.split(' '):
        html = html.replace(word, f'<span class="highlighted">{word}</span>')
    return format_html(html)
