from django import template

register = template.Library()


@register.filter()
def class_name(value):
    """TODO: add docstring."""
    return value.__class__.__name__
