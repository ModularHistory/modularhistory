import logging
from typing import Optional, Union

from django import template
from django.urls import reverse

from core.models.model import ExtendedModel

register = template.Library()


@register.filter()
def get_admin_url(model_instance: Union[dict, ExtendedModel]) -> str:
    """Return the URL of the model instance's admin page."""
    if isinstance(model_instance, dict):
        app, model = model_instance['model'].split('.')
        return reverse(f'admin:{app}_{model}_change', args=[model_instance['id']])
    try:
        return model_instance.get_admin_url()
    except AttributeError as err:
        logging.error(
            f'Using the `get_admin_url` filter on {model_instance} '
            f'(of type {type(model_instance)}) resulted in {err.__class__}: {err}'
        )
        return ''


@register.filter()
def get_detail_url(instance: Union[ExtendedModel, dict]) -> Optional[str]:
    """Return the URL for the model instance's detail page."""
    if isinstance(instance, ExtendedModel):
        return instance.get_absolute_url()
    else:
        try:
            app_label, _ = instance['model'].split('.')
            pk, slug = instance.get('pk'), instance.get('slug')
        except (TypeError, KeyError) as err:
            logging.error(f'{err}')
            return None
    return f'/{app_label}/{slug or pk}'
