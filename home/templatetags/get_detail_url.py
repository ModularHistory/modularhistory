from typing import Optional

from django import template
from django.urls import reverse

from history.models import Model

register = template.Library()


@register.filter()
def get_detail_url(obj: Model) -> Optional[str]:
    """TODO: add docstring."""
    if obj:
        return reverse(f'{obj._meta.app_label}:detail', args=[obj.id])
    return None
