from typing import Dict, Union

from rest_framework import filters

from apps.dates.structures import HistoricDateTime
from apps.search.models import SearchableDatedModel

SORT_BY_PARAM = 'ordering'


class SortByFilterBackend(filters.BaseFilterBackend):
    """
    Filter that sorts queryset by SORT_BY_PARAM
    """
    def filter_queryset(self, request, queryset, view):
        sort_by_date = request.query_params.get(SORT_BY_PARAM) == 'date'

        if sort_by_date:
            return sorted(queryset, key=date_sorter, reverse=False)

        return queryset


def date_sorter(model_instance: Union[SearchableDatedModel, Dict]) -> HistoricDateTime:
    """Return the value used to sort the model instance by date."""
    get_date = getattr(model_instance, 'get_date', None)
    if get_date is not None:
        date = get_date()
    elif isinstance(model_instance, dict):
        date = model_instance.get('date')
    else:
        date = getattr(model_instance, 'date', None)
    if not date:
        date = HistoricDateTime(1, 1, 1, 0, 0, 0)
    # Display precise dates before ranges, e.g., "1500" before "1500 – 2000"
    if getattr(model_instance, 'end_date', None):
        microsecond = date.microsecond + 1
        date = date.replace(microsecond=microsecond)
    return date