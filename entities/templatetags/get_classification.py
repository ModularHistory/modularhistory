from typing import Optional

from django import template

from entities.models import Entity, EntityClassification
from history.structures import HistoricDateTime

register = template.Library()


@register.filter
def get_classification(value: Entity, date: HistoricDateTime) -> Optional[EntityClassification]:
    entity = value
    if not entity:
        return None
    return entity.get_classification(date=date)
