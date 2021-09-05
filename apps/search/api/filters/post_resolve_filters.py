import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union

from rest_framework import filters

from apps.dates.structures import HistoricDateTime
from apps.search.api.search import SEARCHABLE_DOCUMENTS
from apps.search.models import SearchableDatedModel

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.search.documents.base import Document
    from core.models.model import ExtendedModel

QUERY_PARAM = 'query'
SORT_BY_PARAM = 'ordering'


class ApplyMetaFilterBackend(filters.BaseFilterBackend):
    """
    Filter that adds a meta attribute to model instances.

    The meta value comes from the elasticsearch response and contains fields
    like highlight and score.
    """

    def __init__(self):
        """Construct the filter backend."""
        self.view = None

    def filter_queryset(self, request: 'HttpRequest', queryset, view) -> list:
        """Return the filtered queryset."""
        self.view = view
        return list(map(self.apply_meta, queryset))

    def apply_meta(self, model_instance: 'ExtendedModel'):
        """Attach search result meta info to a model instance."""
        document: Optional['Document'] = next(
            (
                document
                for document in SEARCHABLE_DOCUMENTS.values()
                if isinstance(model_instance, document.django.model)
            ),
            None,
        )
        if document:
            index = document.get_index_name()
            key = f'{index}_{model_instance.pk}'
            hit = self.view.search.results_by_id[key]
            model_instance.meta = hit.meta
            return model_instance


class SortByFilterBackend(filters.BaseFilterBackend):
    """Filter that sorts queryset by SORT_BY_PARAM."""

    def filter_queryset(self, request: 'HttpRequest', queryset, view):
        """Return the filtered queryset."""
        query = request.query_params.get(QUERY_PARAM)
        sort_by_date = request.query_params.get(SORT_BY_PARAM) == 'date'
        default_score = 1.0  # The max score is 1.0 when there is no query.
        highest_score = view.search._response.hits.max_score or 0
        score_sortable = query and highest_score > default_score
        sort_by = score_sorter
        reverse = True
        if sort_by_date or not score_sortable:
            sort_by = date_sorter
            reverse = False
        return sorted(queryset, key=sort_by, reverse=reverse)


def date_sorter(model_instance: Union[SearchableDatedModel, dict]) -> datetime:
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
        date = HistoricDateTime(1, 1, 1, 0, 0, 0, microsecond=0)
    # Display precise dates before ranges, e.g., "1500" before "1500 – 2000"
    if getattr(model_instance, 'end_date', None):
        microsecond = date.microsecond + 1
        date = date.replace(microsecond=microsecond)
    return date


def score_sorter(model) -> float:
    """Return the value used to sort the model instance by date."""
    return model.meta.score


def es_sorter(model) -> float:
    """Return the first non-zero sort value from elasticsearch sort array."""
    return list(filter(lambda x: x != 0, model.meta.sort))[0]
