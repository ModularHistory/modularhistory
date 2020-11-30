from typing import Dict, Optional, Union

from django import template
from django.urls import reverse

from modularhistory.models import Model

register = template.Library()


@register.filter()
def get_detail_url(instance: Union[Model, Dict]) -> Optional[str]:
    """Return the URL for the model instance's detail page."""
    if isinstance(instance, Model):
        app_label = instance.get_meta().app_label
        pk = instance.pk
    elif isinstance(instance, dict):
        app_label, _ = instance['model'].split('.')
        pk = instance['pk']
    else:
        return None
    return reverse(f'{app_label}:detail', args=[pk])
