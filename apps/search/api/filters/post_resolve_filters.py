import logging
from typing import Dict, Union

from rest_framework import filters

from apps.dates.structures import HistoricDateTime
from apps.search.api.search import SEARCHABLE_DOCUMENTS
from apps.search.models import SearchableDatedModel

SORT_BY_PARAM = 'ordering'


class ApplyMetaFilterBackend(filters.BaseFilterBackend):
    """
    Filter that applies meta field from elasticsearch response that contains fields like highlight and score.
    """

    def __init__(self):
        self.view = None

    def filter_queryset(self, request, queryset, view):
        self.view = view
        return list(map(self.apply_meta, queryset))

    def apply_meta(self, model):
        document = next(
            (
                document
                for document in SEARCHABLE_DOCUMENTS.values()
                if isinstance(model, document.django.model)
            ),
            None,
        )
        index = document.get_index_name()
        key = f'{index}_{model.pk}'
        hit = self.view.search.results_by_id[key]
        model.meta = hit.meta
        return model


class SortByFilterBackend(filters.BaseFilterBackend):
    """
    Filter that sorts queryset by SORT_BY_PARAM
    """

    def filter_queryset(self, request, queryset, view):
        sort_by_date = request.query_params.get(SORT_BY_PARAM) == 'date'
        score_sortable = (view.search._response.hits.max_score or 0) > 0

        sort_by = score_sorter
        reverse = True

        if sort_by_date:
            sort_by = sort_by_date
            reverse = True
        elif not score_sortable:
            sort_by = es_sorter
            reverse = False

        return sorted(queryset, key=sort_by, reverse=reverse)


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
        logging.error(
            f'{model_instance} has no date attribute but is included in search results.'
        )
        date = HistoricDateTime(1, 1, 1, 0, 0, 0)
    # Display precise dates before ranges, e.g., "1500" before "1500 – 2000"
    if getattr(model_instance, 'end_date', None):
        microsecond = date.microsecond + 1
        date = date.replace(microsecond=microsecond)
    return date


def score_sorter(model) -> float:
    """Return the value used to sort the model instance by date."""
    return model.meta.score


def es_sorter(model) -> float:
    """Return the first non-zero sort value from elasticsearch sort array"""
    return list(filter(lambda x: x != 0, model.meta.sort))[0]
