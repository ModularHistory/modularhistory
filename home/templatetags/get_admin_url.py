from typing import Optional

from django import template

from modularhistory.models import Model

register = template.Library()


@register.filter()
def get_admin_url(obj: Model) -> Optional[str]:
    """TODO: add docstring."""
    if obj:
        if not isinstance(obj, Model):
            raise ValueError(f'Object should be a model but instead is type "{type(obj)}": {obj}')
        return obj.get_admin_url()
    print('>>> ERROR: get_admin_url was called with no `obj` value')
    return None
