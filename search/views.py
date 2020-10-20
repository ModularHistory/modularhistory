# type: ignore
# TODO: stop ignoring types when mypy bug is fixed

"""Views for the search app."""

# from django.shortcuts import render
from itertools import chain
from typing import Dict, List, Optional, Union

from django.db.models import Q, QuerySet, Subquery
from django.views.generic import ListView

from entities.models import Entity
from modularhistory.constants import IMAGE_CT_ID, OCCURRENCE_CT_ID, QUOTE_CT_ID, SOURCE_CT_ID
# from django.core.paginator import Paginator
from modularhistory.models import DatedModel, Model
from modularhistory.structures.historic_datetime import HistoricDateTime
from images.models import Image
from occurrences.models import Occurrence
# from places.models import Place
from quotes.models import Quote
from search.forms import SearchForm
from sources.models import Source
from topics.models import Topic


def date_sorter(model_instance: Union[Model, DatedModel]):
    """TODO: add docstring."""
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
    """TODO: add docstring."""
    rank = getattr(model_instance, 'rank', None)
    if not rank:
        raise Exception('No rank')
    print(f'>>> {rank}: {model_instance}\n')
    return rank


# TODO: https://docs.djangoproject.com/en/3.0/topics/db/search/
# TODO: https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/
class SearchResultsView(ListView):
    """TODO: add docstring."""

    template_name = 'search/search_results.html'
    results_count = 0
    paginate_by = 10

    excluded_content_types: Optional[List[int]] = None
    sort_by_relevance: bool = False
    suppress_unverified: bool = True
    entities: Optional[QuerySet] = None
    topics: Optional[QuerySet] = None
    places: Optional[QuerySet] = None
    db: str = 'default'

    def get_context_data(self, *args, **kwargs) -> Dict:
        """TODO: add docstring."""
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.results_count or 0
        query = self.request.GET.get('query')
        context['query'] = query

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
            # places=self.places
            entities=self.entities,
            topics=self.topics,
            # initial=data
        )
        context['search_form'] = search_form
        # context['object_list'] = self.get_object_list()
        return context

    def get_object_list(self) -> Union[QuerySet, List]:
        """TODO: add docstring."""
        request = self.request
        query = request.GET.get('query', None)

        db = self.db

        sort_by_relevance = request.GET.get('ordering') == 'relevance'
        self.sort_by_relevance = sort_by_relevance

        suppress_unverified = request.GET.get('quality') != 'unverified'
        self.suppress_unverified = suppress_unverified

        ct_ids = [int(ct_id) for ct_id in (request.GET.getlist('content_types') or [])]
        start_year = request.GET.get('start_year_0', None)
        year_type = request.GET.get('start_year_1', None)
        if start_year and year_type:
            pass
            # TODO: Create historic datetime obj from year and year type
        end_year = request.GET.get('end_year_0', None)

        entities = request.GET.getlist('entities', None)
        entity_ids = [int(entity) for entity in entities] if entities else None

        topics = request.GET.getlist('topics', None)
        topic_ids = [int(topic) for topic in topics] if topics else None

        search_kwargs = {
            'query': query,
            'start_year': start_year,
            'end_year': end_year,
            'rank': sort_by_relevance,
            'suppress_unverified': suppress_unverified,
            'db': db,
            'entity_ids': entity_ids,
            'topic_ids': topic_ids
        }

        # Occurrences
        occurrence_result_ids = []
        if OCCURRENCE_CT_ID in ct_ids or not ct_ids:
            occurrence_results = Occurrence.objects.search(**search_kwargs)
            occurrence_result_ids = [occurrence.id for occurrence in occurrence_results]
        else:
            occurrence_results = Occurrence.objects.none()

        # Quotes
        quote_result_ids = []
        if QUOTE_CT_ID in ct_ids or not ct_ids:
            quote_results = Quote.objects.search(**search_kwargs)
            if occurrence_results:
                # TODO: refactor
                quote_results = quote_results.exclude(
                    Q(relations__content_type_id=OCCURRENCE_CT_ID) &
                    Q(relations__object_id__in=occurrence_result_ids)
                )
            quote_result_ids = [quote.id for quote in quote_results]
        else:
            quote_results = Quote.objects.using(db).none()

        # Images
        if IMAGE_CT_ID in ct_ids or not ct_ids:
            image_results = Image.objects.search(**search_kwargs).filter(entities=None)
            if occurrence_results:
                image_results = image_results.exclude(
                    Q(occurrences__in=occurrence_results) |
                    Q(entities__involved_occurrences__in=occurrence_results)
                )
            if quote_results:
                image_results = image_results.exclude(entities__quotes__in=quote_results)
        else:
            image_results = Image.objects.using(db).none()

        # Sources
        if SOURCE_CT_ID in ct_ids or not ct_ids:
            source_results = Source.objects.search(**search_kwargs)
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
            source_results = Source.objects.using(db).none()

        entity_subquery = Subquery(
            Entity.objects.filter(
                Q(involved_occurrences__in=occurrence_results) |
                Q(quotes__in=quote_results) |
                Q(attributed_sources__in=source_results)
            ).order_by('id').distinct('id').values('pk')
        )
        self.entities = Entity.objects.using(db).filter(pk__in=entity_subquery).order_by('name')

        # # occurrence topic relations
        # for topic_id in TopicRelation.objects.filter(
        #     Q(content_type_id=OCCURRENCE_CT_ID) & Q(object_id__in=occurrence_result_ids)
        # ).values_list('topic_id', flat=True).distinct():
        #     print(topic_id)
        #     topics_ids.append(topic_id)
        #
        # # quote topic relations
        # for topic_id in TopicRelation.objects.filter(
        #     Q(content_type_id=QUOTE_CT_ID) & Q(object_id__in=quote_result_ids)
        # ).values_list('topic_id', flat=True).distinct():
        #     print(topic_id)
        #     topics_ids.append(topic_id)

        self.topics = Topic.objects.using(db).filter(
            Q(
                topic_relations__content_type_id=QUOTE_CT_ID,
                topic_relations__object_id__in=quote_result_ids
            ) |
            Q(
                topic_relations__content_type_id=OCCURRENCE_CT_ID,
                topic_relations__object_id__in=occurrence_result_ids
            )
        ).order_by('key').distinct()

        # self.places = Place.objects.filter(
        #     Q(occurrences__in=occurrence_results)
        #     | Q(publications__in=source_results)
        # ).distinct

        # Combine querysets
        queryset_chain = chain(
            occurrence_results,
            quote_results,
            image_results,
            source_results
        )

        # Order the results
        key = rank_sorter if sort_by_relevance else date_sorter
        qs = sorted(queryset_chain, key=key, reverse=False)

        self.results_count = len(qs)

        return qs

    def get_queryset(self) -> QuerySet:
        """
        Required because SearchResultsView inherits from the generic Django ListView.

        Returns an empty queryset.

        SearchResultsView uses `get_object_list` instead of `get_queryset` to set
        the context variable containing the list of search results.
        """
        return self.get_object_list()
