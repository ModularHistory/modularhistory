import logging
from typing import Dict, Optional, Union

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


@register.filter()
def get_detail_url(instance: Union[Model, Dict]) -> Optional[str]:
    """Return the URL for the model instance's detail page."""
    if isinstance(instance, Model):
        app_label = instance.get_meta().app_label
        pk = instance.pk
    else:
        try:
            app_label, _ = instance['model'].split('.')
            pk = instance['pk']
        except (TypeError, KeyError) as err:
            logging.error(f'{err}')
            return None
    return reverse(f'{app_label}:detail', args=[pk])
