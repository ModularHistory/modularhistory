"""
Module for get_categorization_string custom template filter.

See Django docs:
https://docs.djangoproject.com/en/3.1/howto/custom-template-tags/#writing-custom-template-filters
"""

from typing import Optional

from django import template

from apps.entities.models import Entity
from core.structures import HistoricDateTime

register = template.Library()


@register.filter
def get_categorization_string(entity: Entity, date: HistoricDateTime) -> Optional[str]:
    """
    Return the entity's categorization string.

    This filter can be used in templates like so:
        {% load get_categorization_string %}
        ...
        <span>{{ entity|get_categorization_string:date }}</span>
    """
    if not entity:
        return None
    return entity.get_categorization_string(date=date)
