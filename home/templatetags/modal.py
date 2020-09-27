from django import template

register = template.Library()


@register.inclusion_tag('_modal.html')
def modal():
    """TODO: add docstring."""
    return {}
