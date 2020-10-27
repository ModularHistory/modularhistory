"""Views for the search app."""

import logging
from itertools import chain
from typing import Dict, List, Optional, Union

from django.db.models import Q, QuerySet, Subquery
from django.views.generic import ListView

from entities.models import Entity
from images.models import Image
from modularhistory.constants import (
    IMAGE_CT_ID,
    OCCURRENCE_CT_ID,
    QUOTE_CT_ID,
    SOURCE_CT_ID,
)
from modularhistory.models import DatedModel, Model
from modularhistory.structures.historic_datetime import HistoricDateTime
from occurrences.models import Occurrence
from quotes.models import Quote
from search.forms import SearchForm
from sources.models import Source
from topics.models import Topic

QUERY_KEY = 'query'


def date_sorter(model_instance: Union[Model, DatedModel]) -> HistoricDateTime:
    """Return the value used to sort the model instance by date."""
    get_date = getattr(model_instance, 'get_date', None)
    if get_date is not None:
        date = get_date()
    else:
        date = getattr(model_instance, 'date', None)
    if not date:
        date = HistoricDateTime(1, 1, 1, 0, 0, 0)
    # Display precise dates before ranges, e.g., "1500" before "1500 – 2000"
    if getattr(model_instance, 'end_date', None):
        microsecond = date.microsecond + 1
        date = date.replace(microsecond=microsecond)
    return date


def rank_sorter(model_instance: Model):
    """Return the value used to sort the model instance by rank/relevance."""
    rank = getattr(model_instance, 'rank', None)
    if not rank:
        raise Exception('No rank')
    logging.info(f'>>> {rank}: {model_instance}\n')
    return rank


# TODO: https://docs.djangoproject.com/en/3.0/topics/db/search/
# TODO: https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/
class SearchResultsView(ListView):
    """View that displays search results."""

    template_name = 'search/search_results.html'
    paginate_by = 10

    excluded_content_types: Optional[List[int]]
    sort_by_relevance: bool
    suppress_unverified: bool
    entities: Optional[QuerySet]
    topics: Optional[QuerySet]
    places: Optional[QuerySet]
    results_count: int

    def __init__(self):
        """Construct the search results view."""
        super().__init__()
        self.excluded_content_types = None
        self.sort_by_relevance = False
        self.suppress_unverified = True
        self.entities = None
        self.topics = None
        self.places = None
        self.results_count = 0

    def get_context_data(self, *args, **kwargs) -> Dict:
        """Return the context data used to render the view."""
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.results_count or 0
        query = self.request.GET.get(QUERY_KEY)
        context[QUERY_KEY] = query

        # Initial data
        # data = {
        #     'content_types': None,
        #     'entities': None,
        #     'topics': None,
        # }
        search_form = SearchForm(
            request=self.request,
            query=query,
            suppress_unverified=self.suppress_unverified,
            order_by_relevance=self.sort_by_relevance,
            excluded_content_types=self.excluded_content_types,
            entities=self.entities,
            topics=self.topics,
            # initial=data
        )
        context['search_form'] = search_form
        return context

    def get_object_list(self) -> Union['QuerySet[Model]', List[Model]]:
        """Return the list of search result objects."""
        request = self.request
        self.sort_by_relevance = request.GET.get('ordering') == 'relevance'
        self.suppress_unverified = request.GET.get('quality') != 'unverified'

        ct_ids = [int(ct_id) for ct_id in (request.GET.getlist('content_types') or [])]
        start_year = request.GET.get('start_year_0', None)
        year_type = request.GET.get('start_year_1', None)
        if start_year and year_type:
            # TODO: Create historic datetime obj from year and year type
            pass

        entities = request.GET.getlist('entities', None)
        entity_ids = [int(entity_id) for entity_id in entities] if entities else None

        topics = request.GET.getlist('topics', None)
        topic_ids = [int(topic_id) for topic_id in topics] if topics else None

        search_kwargs = {
            QUERY_KEY: request.GET.get(QUERY_KEY, None),
            'start_year': start_year,
            'end_year': request.GET.get('end_year_0', None),
            'rank': self.sort_by_relevance,
            'suppress_unverified': self.suppress_unverified,
            'db': self.db,
            'entity_ids': entity_ids,
            'topic_ids': topic_ids,
        }

        occurrence_results, occurrence_result_ids = _get_occurrence_results(
            ct_ids, **search_kwargs
        )
        quote_results, quote_result_ids = _get_quote_results(ct_ids, **search_kwargs)
        image_results = _get_image_results(ct_ids, **search_kwargs)
        source_results = _get_source_results(ct_ids, **search_kwargs)

        self.entities = Entity.objects.filter(
            pk__in=Subquery(
                Entity.objects.filter(
                    Q(involved_occurrences__in=occurrence_results)
                    | Q(quotes__in=quote_results)
                    | Q(attributed_sources__in=source_results)
                )
                .order_by('id')
                .distinct('id')
                .values('pk')
            )
        )

        # # occurrence topic relations
        # for topic_id in TopicRelation.objects.filter(
        #     Q(content_type_id=OCCURRENCE_CT_ID) & Q(object_id__in=occurrence_result_ids)
        # ).values_list('topic_id', flat=True).distinct():
        #     logging.info(topic_id)
        #     topics_ids.append(topic_id)
        #
        # # quote topic relations
        # for topic_id in TopicRelation.objects.filter(
        #     Q(content_type_id=QUOTE_CT_ID) & Q(object_id__in=quote_result_ids)
        # ).values_list('topic_id', flat=True).distinct():
        #     logging.info(topic_id)
        #     topics_ids.append(topic_id)

        self.topics = (
            Topic.objects.using(self.db)
            .filter(
                Q(
                    topic_relations__content_type_id=QUOTE_CT_ID,
                    topic_relations__object_id__in=quote_result_ids,
                )
                | Q(
                    topic_relations__content_type_id=OCCURRENCE_CT_ID,
                    topic_relations__object_id__in=occurrence_result_ids,
                )
            )
            .order_by('key')
            .distinct()
        )

        # self.places = Place.objects.filter(
        #     Q(occurrences__in=occurrence_results)
        #     | Q(publications__in=source_results)
        # ).distinct

        ordered_queryset = self.order_queryset(
            # Combine querysets
            chain(occurrence_results, quote_results, image_results, source_results)
        )

        self.results_count = len(ordered_queryset)

        return ordered_queryset

    def order_queryset(self, queryset_chain):
        """Return an ordered queryset based on a queryset chain."""
        key = rank_sorter if self.sort_by_relevance else date_sorter
        return sorted(queryset_chain, key=key, reverse=False)

    def get_queryset(self) -> QuerySet:
        """
        Return the queryset/list of model instances.

        Required because SearchResultsView inherits from the generic Django ListView.

        SearchResultsView uses `get_object_list` instead of `get_queryset` to set
        the context variable containing the list of search results.
        """
        return self.get_object_list()


def _get_occurrence_results(ct_ids, **search_kwargs):
    # Occurrences
    occurrence_result_ids = []
    if OCCURRENCE_CT_ID in ct_ids or not ct_ids:
        occurrence_results = Occurrence.objects.search(**search_kwargs)  # type: ignore
        occurrence_result_ids = [occurrence.id for occurrence in occurrence_results]
    else:
        occurrence_results = Occurrence.objects.none()
    return occurrence_results, occurrence_result_ids


def _get_quote_results(
    ct_ids, occurrence_results, occurrence_result_ids, **search_kwargs
):
    quote_result_ids = []
    if QUOTE_CT_ID in ct_ids or not ct_ids:
        quote_results = Quote.objects.search(**search_kwargs)  # type: ignore
        if occurrence_results:
            # TODO: refactor
            quote_results = quote_results.exclude(
                Q(relations__content_type_id=OCCURRENCE_CT_ID)
                & Q(relations__object_id__in=occurrence_result_ids)
            )
        quote_result_ids = [quote.id for quote in quote_results]
    else:
        quote_results = Quote.objects.none()
    return quote_results, quote_result_ids


def _get_image_results(ct_ids, occurrence_results, quote_results, **search_kwargs):
    if IMAGE_CT_ID in ct_ids or not ct_ids:
        image_results = Image.objects.search(**search_kwargs).filter(  # type: ignore
            entities=None
        )
        if occurrence_results:
            image_results = image_results.exclude(
                Q(occurrences__in=occurrence_results)
                | Q(entities__involved_occurrences__in=occurrence_results)
            )
        if quote_results:
            image_results = image_results.exclude(entities__quotes__in=quote_results)
    else:
        image_results = Image.objects.none()
    return image_results


def _get_source_results(ct_ids, **search_kwargs):
    if SOURCE_CT_ID in ct_ids or not ct_ids:
        source_results = Source.objects.search(**search_kwargs)  # type: ignore
        # TODO: This was broken by conversion to generic relations with quotes & occurrences
        # source_results = source_results.exclude(
        #     Q(occurrences__in=occurrence_results) |
        #     Q(quotes__related_occurrences__in=occurrence_results) |
        #     Q(contained_sources__occurrences__in=occurrence_results) |
        #     Q(contained_sources__quotes__related_occurrences__in=occurrence_results) |
        #     Q(quotes__in=quote_results) |
        #     Q(contained_sources__quotes__in=quote_results)
        # )
    else:
        source_results = Source.objects.none()
    return source_results
