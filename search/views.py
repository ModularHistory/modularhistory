# from django.shortcuts import render
from itertools import chain
from typing import Dict, List, Optional, Tuple, Union

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet, Subquery
from django.views.generic import ListView

from entities.models import Entity
# from django.core.paginator import Paginator
from history.models import Model, DatedModel
from history.structures.historic_datetime import HistoricDateTime
from images.models import Image
from occurrences.models import Occurrence
# from places.models import Place
from quotes.models import Quote
from search.forms import SearchFilterForm
from sources.models import Source
from topics.models import Topic


def date_sorter(x: Union[Model, DatedModel]):
    date = None
    if hasattr(x, 'get_date'):
        date = x.get_date()
    elif hasattr(x, 'date'):
        date = x.date
    if not date:
        date = HistoricDateTime(1, 1, 1, 0, 0, 0)

    # Display precise dates before ranges, e.g., "1500" before "1500 – 2000"
    if hasattr(x, 'end_date') and getattr(x, 'end_date'):
        date = date.replace(microsecond=date.microsecond+1)

    return date


def rank_sorter(x: Union[Model]):
    if not hasattr(x, 'rank'):
        raise Exception('No rank')
    print(f'>>> {x.rank}: {x}\n')
    return getattr(x, 'rank')


# TODO: https://docs.djangoproject.com/en/3.0/topics/db/search/
# TODO: https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/
class SearchResultsView(ListView):
    template_name = 'search/search_results.html'
    results_count = 0
    paginate_by = 100

    content_types: Optional[List[Tuple[int, str]]] = None
    sort_by_relevance: bool = False
    suppress_unverified: bool = True
    entities: Optional[QuerySet] = None
    topics: Optional[QuerySet] = None
    places: Optional[QuerySet] = None
    db: str = 'default'

    def get_context_data(self, *args, **kwargs) -> Dict:
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

        search_filter_form = SearchFilterForm(
            request=self.request,
            query=query,
            suppress_unverified=self.suppress_unverified,
            order_by_relevance=self.sort_by_relevance,
            content_types=self.content_types,
            # places=self.places
            entities=self.entities,
            topics=self.topics,
            # initial=data
        )
        context['search_filter_form'] = search_filter_form
        return context

    def get_queryset(self) -> Union[QuerySet, List]:
        request = self.request
        query = request.GET.get('query', None)

        db = self.db

        sort_by_relevance = request.GET.get('ordering') == 'relevance'
        self.sort_by_relevance = sort_by_relevance

        suppress_unverified = not request.GET.get('quality') == 'unverified'
        self.suppress_unverified = suppress_unverified

        ct_ids = request.GET.getlist('content_types', None)
        start_year = request.GET.get('start_year_0', None)
        year_type = request.GET.get('start_year_1', None)
        if start_year and year_type:
            pass
            # TODO: Create historic datetime object from year and year type
        end_year = request.GET.get('end_year_0', None)
        entity_ids = request.GET.getlist('entities', None)
        topic_ids = request.GET.getlist('topics', None)
        content_types = []
        for ct_id in ct_ids:
            ct = ContentType.objects.get_for_id(ct_id).model_class()
            content_types.append(ct)

        search_kwargs = {
            'query': query,
            'start_year': start_year,
            'end_year': end_year,
            'rank': sort_by_relevance,
            'suppress_unverified': suppress_unverified,
            'db': db
        }

        # Occurrences
        if Occurrence in content_types or not content_types:
            occurrence_results = Occurrence.objects.search(
                **search_kwargs,
                entity_ids=entity_ids,
                topic_ids=topic_ids,
            )
        else:
            occurrence_results = Occurrence.objects.none()

        # Quotes
        if Quote in content_types or not content_types:
            quote_results = Quote.objects.search(
                **search_kwargs,
                entity_ids=entity_ids,
                topic_ids=topic_ids
            )
            if occurrence_results:
                quote_results = quote_results.exclude(related_occurrences__in=occurrence_results)
        else:
            quote_results = Quote.objects.using(db).none()

        # Images
        if Image in content_types or not content_types:
            image_results = Image.objects.search(
                **search_kwargs,
                entity_ids=entity_ids,
                topic_ids=topic_ids
            ).filter(entities=None)
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
        if Source in content_types or not content_types:
            source_results = Source.objects.search(
                **search_kwargs,
                entity_ids=entity_ids,
                topic_ids=topic_ids
            )
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

        self.entities = Entity.objects.using(db).filter(pk__in=Subquery(Entity.objects.filter(
            Q(involved_occurrences__in=occurrence_results) |
            Q(quotes__in=quote_results) |
            Q(attributed_sources__in=source_results)
        ).order_by('id').distinct('id').values('pk'))).order_by('name')
        self.topics = Topic.objects.using(db).filter(pk__in=Subquery(Topic.objects.filter(
            Q(related_occurrences__in=occurrence_results) |
            Q(related_quotes__in=quote_results)
            # | Q(related_topics__related_quotes__in=quote_results)
        ).order_by('id').distinct('id').values('pk'))).order_by('key')
        # self.places = Place.objects.filter(
        #     Q(occurrences__in=occurrence_results)
        #     | Q(publications__in=source_results)
        # ).distinct

        # Content types
        content_types = []
        if len(occurrence_results):
            content_types.append((ContentType.objects.get_for_model(Occurrence).id, 'Occurrences'))
        if len(quote_results):
            content_types.append((ContentType.objects.get_for_model(Quote).id, 'Quotes'))
        if len(image_results):
            content_types.append((ContentType.objects.get_for_model(Image).id, 'Images'))
        if len(source_results):
            content_types.append((ContentType.objects.get_for_model(Source).id, 'Sources'))
        self.content_types = content_types

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
