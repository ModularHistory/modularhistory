from django import template

register = template.Library()


@register.inclusion_tag('_modal.html')
def modal():
    """Loads modal HTML into a template."""
    return {}
