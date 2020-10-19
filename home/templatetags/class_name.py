from django import template

register = template.Library()


@register.filter()
def class_name(instance):
    """TODO: add docstring."""
    return instance.__class__.__name__
