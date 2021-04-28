import logging
from itertools import chain
from typing import Dict, List, Optional, Union

from django.db.models import Q, QuerySet, Subquery
from rest_framework.generics import ListAPIView

from apps.dates.structures import HistoricDateTime
from apps.entities.models import Entity
from apps.images.models import Image
from apps.occurrences.models import Occurrence
from apps.quotes.models import Quote
from apps.search.models import SearchableDatedModel
from apps.sources.models import Source
from apps.topics.models import Topic
from core.constants.content_types import ContentTypes, get_ct_id

QUERY_KEY = 'query'
N_RESULTS_PER_PAGE = 10


class SearchResultsSerializer:
    def __init__(self, queryset, *args, **kwargs):
        self.data = [instance.serialize() for instance in queryset]


class SearchResultsAPIView(ListAPIView):
    """API view for listing search results."""

    serializer_class = SearchResultsSerializer
    template_name = 'search/search_results.html'
    paginate_by = N_RESULTS_PER_PAGE

    excluded_content_types: Optional[List[str]]
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
        self.suppress_unverified = False
        self.entities = None
        self.topics = None
        self.places = None
        self.results_count = 0

    def order_queryset(self, queryset_chain):
        """Return an ordered queryset based on a queryset chain."""
        key = rank_sorter if self.sort_by_relevance else date_sorter
        return sorted(queryset_chain, key=key, reverse=False)

    def get_queryset(self) -> QuerySet:
        """
        Return the queryset/list of model instances.

        Required because SearchResultsView inherits from the generic Django ListView.
        """
        request = self.request
        self.sort_by_relevance = request.query_params.get('ordering') == 'relevance'
        self.suppress_unverified = request.query_params.get('quality') == 'verified'

        content_types = request.query_params.getlist('content_types') or []

        start_year = request.query_params.get('start_year', None)
        # start_year_type = request.query_params.get('start_year_type', None)
        end_year = request.query_params.get('end_year', None)
        # end_year_type = request.query_params.get('end_year_type', None)

        # if start_year and start_year_type:
        # TODO: Create historic datetime obj from year and year type

        entities = request.query_params.getlist('entities', None)
        entity_ids = [int(entity_id) for entity_id in entities] if entities else None

        topics = request.query_params.getlist('topics', None)
        topic_ids = [int(topic_id) for topic_id in topics] if topics else None

        search_kwargs = {
            QUERY_KEY: request.query_params.get(QUERY_KEY, None),
            'start_year': start_year,
            'end_year': end_year,
            'entity_ids': entity_ids,
            'topic_ids': topic_ids,
            'rank': self.sort_by_relevance,
            'suppress_unverified': self.suppress_unverified,
            'suppress_hidden': True,
        }

        occurrence_results, occurrence_result_ids = _get_occurrence_results(
            content_types, **search_kwargs
        )
        quote_results, quote_result_ids = _get_quote_results(
            content_types, occurrence_result_ids, **search_kwargs
        )
        source_results, source_result_ids = _get_source_results(
            content_types, occurrence_result_ids, quote_result_ids, **search_kwargs
        )

        # TODO
        fixed = False
        if fixed:
            image_results = _get_image_results(
                content_types, occurrence_result_ids, quote_result_ids, **search_kwargs
            )

        self.entities = Entity.objects.filter(
            pk__in=Subquery(
                Entity.objects.filter(
                    Q(involved_occurrences__id__in=occurrence_result_ids)
                    | Q(quotes__id__in=quote_result_ids)
                    # | Q(attributed_sources__id__in=source_result_ids)
                )
                .order_by('id')
                .distinct('id')
                .values('pk')
            )
        )

        self.topics = (
            Topic.objects.filter(
                Q(
                    topic_relations__content_type_id=get_ct_id(ContentTypes.quote),
                    topic_relations__object_id__in=quote_result_ids,
                )
                | Q(
                    topic_relations__content_type_id=get_ct_id(ContentTypes.occurrence),
                    topic_relations__object_id__in=occurrence_result_ids,
                )
            )
            .order_by('name')
            .distinct()
        )

        ordered_queryset = self.order_queryset(
            # Combine querysets
            chain(
                occurrence_results,
                quote_results,
            )  # , image_results)  # , source_results)
        )

        self.results_count = len(ordered_queryset)
        return ordered_queryset


def _get_occurrence_results(content_types, **search_kwargs):
    if ContentTypes.occurrence in content_types or not content_types:
        occurrence_results = list(Occurrence.objects.search(**search_kwargs).iterator())
    else:
        occurrence_results = []
    return occurrence_results, [
        occurrence.pk for occurrence in occurrence_results if occurrence
    ]


def _get_quote_results(content_types, occurrence_result_ids, **search_kwargs):
    if ContentTypes.quote in content_types or not content_types:
        quote_results = Quote.objects.search(**search_kwargs)  # type: ignore
        if occurrence_result_ids:
            # TODO: refactor
            quote_results = quote_results.exclude(
                Q(relations__content_type_id=get_ct_id(ContentTypes.occurrence))
                & Q(relations__object_id__in=occurrence_result_ids)
            )
        quote_results = list(quote_results.iterator())
    else:
        quote_results = []
    return quote_results, [quote.pk for quote in quote_results if quote]


def _get_image_results(
    content_types, occurrence_result_ids, quote_result_ids, **search_kwargs
):
    if ContentTypes.image in content_types or not content_types:
        image_results = Image.objects.search(**search_kwargs).filter(  # type: ignore
            entities=None
        )
        if occurrence_result_ids:
            image_results = image_results.exclude(
                Q(occurrences__id__in=occurrence_result_ids)
                | Q(entities__involved_occurrences__id__in=occurrence_result_ids)
            )
        if quote_result_ids:
            image_results = image_results.exclude(
                entities__quotes__id__in=quote_result_ids
            )
        image_results = list(image_results.iterator())
    else:
        image_results = []
    return image_results


def _get_source_results(
    content_types, occurrence_result_ids, quote_result_ids, **search_kwargs
):
    if ContentTypes.source in content_types or not content_types:
        source_results = Source.objects.search(**search_kwargs)  # type: ignore

        # TODO: This was broken by conversion to generic relations with quotes & occurrences
        not_broken = False
        if not_broken:
            source_results = source_results.exclude(
                Q(occurrences__id__in=occurrence_result_ids)
                | Q(quotes__related_occurrences__id__in=occurrence_result_ids)
                | Q(contained_sources__occurrences__id__in=occurrence_result_ids)
                | Q(
                    contained_sources__quotes__related_occurrences__id__in=occurrence_result_ids
                )
                | Q(quotes__id__in=quote_result_ids)
                | Q(contained_sources__quotes__id__in=quote_result_ids)
            )
        source_results = list(source_results.iterator())
    else:
        source_results = []
    return source_results, [source.pk for source in source_results if source]


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


def rank_sorter(model_instance: SearchableDatedModel):
    """Return the value used to sort the model instance by rank/relevance."""
    rank = getattr(model_instance, 'rank', None)
    if not rank:
        raise Exception('No rank')
    logging.debug(f'{rank}: {model_instance}\n')
    return rank
