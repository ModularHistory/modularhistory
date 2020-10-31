from typing import Optional

from django import template
from django.urls import reverse

from modularhistory.models import Model
from typing import Union, Dict

register = template.Library()


@register.filter()
def get_detail_url(instance) -> Optional[str]:
    """Return the URL for the model instance's detail page."""
    if isinstance(instance, Model):
        model_instance = instance
    else:
        model_instance = instance.instance
    if model_instance:
        return reverse(
            f'{model_instance.get_meta().app_label}:detail', args=[model_instance.id]
        )
    return None
