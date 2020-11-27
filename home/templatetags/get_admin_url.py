from typing import Dict, Union

from django import template
from django.urls import reverse

from modularhistory.models import Model

register = template.Library()


@register.filter()
def get_admin_url(model_instance: Union[Dict, Model]) -> str:
    """Return the URL of the model instance's admin page."""
    if isinstance(model_instance, dict):
        app, model = model_instance['model'].split('.')
        return reverse(f'admin:{app}_{model}_change', args=[model_instance['pk']])
    return model_instance.get_admin_url()
