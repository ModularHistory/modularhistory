from django import template

register = template.Library()


@register.filter()
def class_name(instance) -> str:
    """Return the instance's class name."""
    return instance.__class__.__name__
