from typing import Optional

from django import template
from django.urls import reverse

from modularhistory.models import Model

register = template.Library()


@register.filter()
def get_detail_url(model_instance: Model) -> Optional[str]:
    """Return the URL for the model instance's detail page."""
    if model_instance:
        return reverse(
            f'{model_instance.get_meta().app_label}:detail', args=[model_instance.id]
        )
    return None
