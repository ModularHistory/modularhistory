from django import template

# from sys import stderr
from history.models import Model

register = template.Library()


@register.filter()
def get_admin_url(obj: Model):
    if not isinstance(obj, Model):
        raise ValueError(f'Object should be a model but instead is type "{type(obj)}": {obj}')
    return obj.get_admin_url()
