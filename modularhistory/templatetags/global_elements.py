from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('_footer.html')
def global_footer():
    """Load global footer HTML into a template."""
    return {}


@register.inclusion_tag('_navbar.html')
def global_navbar(user):
    """Load global navbar HTML into a template."""
    return {'user': user, 'settings': settings}
