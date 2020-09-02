from typing import Optional

from django import template

from entities.models import Entity
from history.structures import HistoricDateTime

register = template.Library()


@register.filter
def get_categorization_string(value: Entity, date: HistoricDateTime) -> Optional[str]:
    """TODO: add docstring."""
    entity = value
    if not entity:
        return None
    return entity.get_categorization_string(date=date)
