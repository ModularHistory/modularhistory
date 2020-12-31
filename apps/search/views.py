"""Views for the search app."""

import json
import logging
from http import client
from itertools import chain
from pprint import pformat
from typing import Any, Dict, List, Optional, Union
from modularhistory.constants.content_types import get_ct_id, ContentTypes

from django.conf import settings
from django.db.models import Q, QuerySet, Subquery
from django.http import JsonResponse
from django.views.generic import ListView
from meta.views import Meta

from apps.entities.models import Entity
from apps.images.models import Image
from apps.occurrences.models import Occurrence
from apps.quotes.models import Quote
from apps.search.forms import SearchForm
from apps.search.models import SearchableDatedModel
from apps.sources.models import Source
from apps.topics.models import Topic
from modularhistory.constants.content_types import ModelNameSet

from modularhistory.models import Model
from modularhistory.structures.historic_datetime import HistoricDateTime

QUERY_KEY = 'query'
N_RESULTS_PER_PAGE = 10


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


def _words_api(word: str) -> Dict:
    """
    Pass a request to Words API and return the parsed results as a dictionary.

    Example response from Words API:
    {
        'word': 'opinion',
        'definitions': [
            {
                'definition': "the reason for a court's judgment",
                'partOfSpeech': 'noun'
            },
            {
                'definition': 'the legal document stating the reasons for a judicial decision',
                'partOfSpeech': 'noun'
            },
            {
                'definition': 'a personal belief not founded on proof or certainty',
                'partOfSpeech': 'noun'
            }
        ]
    }

    Example return value:
    {
        'word': 'opinion',
        'meanings': {
            'noun': {
                'definitions': [
                    {
                        'definition': "the reason for a court's judgment"
                    },
                    {
                        'definition': 'the legal document stating the reasons for a judicial decision'
                    },
                    {
                        'definition': 'a personal belief not founded on proof or certainty'
                    }
                ]
            }
        }
    }
    """
    host = 'wordsapiv1.p.rapidapi.com'
    request_url = f'/words/{word}/definitions'
    headers = {
        'x-rapidapi-key': settings.RAPIDAPI_KEY,
        'x-rapidapi-host': host,
    }
    connection = client.HTTPSConnection(host)  # noqa: S309
    connection.request('GET', request_url, headers=headers)
    logging.debug(f'Made Words API request to {request_url}...')
    data = json.loads(connection.getresponse().read().decode('utf-8'))
    logging.info(f'Received response from Words API: {data}')
    parsed_data: Dict[str, Any] = {}
    for result in data.get('definitions', []):
        part_of_speech = result['partOfSpeech']
        definition = {'definition': result['definition']}
        if parsed_data.get(part_of_speech):
            parsed_data[part_of_speech].append(definition)
        else:
            parsed_data[part_of_speech] = [definition]
    return parsed_data


def _google_dict_api(word: str) -> Dict:
    """
    Return a response from Google Dictionary API.

    Example response:
    [
        {
            "word": "opinion",
            "phonetics": [
                {
                    "text": "/həˈloʊ/",
                    "audio": "https://lex-audio.useremarkable.com/mp3/hello_us_1_rr.mp3"
                },
                {
                    "text": "/hɛˈloʊ/",
                    "audio": "https://lex-audio.useremarkable.com/mp3/hello_us_2_rr.mp3"
                }
            ],
            "meanings": [
                {
                    "partOfSpeech": "exclamation",
                    "definitions": [
                        {
                            "definition": "Used as a greeting or to begin a phone conversation.",
                            "example": "hello there, Katie!"
                        }
                    ]
                },
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "An utterance of “hello”; a greeting.",
                            "example": "she was getting polite nods and hellos from people",
                            "synonyms": [
                                "greeting",
                                "welcome",
                                "salutation",
                                "saluting",
                                "hailing",
                                "address",
                                "hello",
                                "hallo"
                            ]
                        }
                    ]
                },
                {
                    "partOfSpeech": "intransitive verb",
                    "definitions": [
                        {
                            "definition": "Say or shout “hello”; greet someone.",
                            "example": "I pressed the phone button and helloed"
                        }
                    ]
                }
            ]
        }
    ]

    """
    host = 'api.dictionaryapi.dev'
    request_url = f'/api/v2/entries/en/{word}'
    connection = client.HTTPSConnection(host)  # noqa: S309
    connection.request('GET', request_url)
    data = json.loads(connection.getresponse().read().decode('utf-8'))
    logging.info(f'Received response from Google Dictionary API: {pformat(data)}')
    return data


def word_search(request, word: str) -> JsonResponse:
    """
    Pass a request to Words API and return the results as JSON.
    """
    use_words_api = True
    if use_words_api:
        data = _words_api(word)
    else:
        data = _google_dict_api(word)
    return JsonResponse(data)


# TODO: https://docs.djangoproject.com/en/3.0/topics/db/search/
# TODO: https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/
class SearchResultsView(ListView):
    """View that displays search results."""

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

    def get_context_data(self, *args, **kwargs) -> Dict:
        """Return the context data used to render the view."""
        context = super().get_context_data(*args, **kwargs)
        context['object_list'] = [
            instance.serialize() for instance in context['object_list'] if instance
        ]
        context['count'] = self.results_count or 0
        query = self.request.GET.get(QUERY_KEY)
        context[QUERY_KEY] = query

        initial_data: Dict[str, Any] = {}
        search_form = SearchForm(
            request=self.request,
            query=query,
            suppress_unverified=self.suppress_unverified,
            order_by_relevance=self.sort_by_relevance,
            excluded_content_types=self.excluded_content_types,
            entities=self.entities,
            topics=self.topics,
            initial=initial_data,
        )
        context['search_form'] = search_form
        title = f'{query or "Historical"} occurrences, quotes, sources, and more | ModularHistory'
        context['meta'] = Meta(
            title=title,
            description=(
                f'{title}, filterable by topic, date, entity, and content type.'
            ),
        )
        return context

    def get_object_list(self) -> Union['QuerySet[Model]', List['Model']]:
        """Return the list of search result objects."""
        request = self.request
        self.sort_by_relevance = request.GET.get('ordering') == 'relevance'
        self.suppress_unverified = request.GET.get('quality') == 'verified'

        content_types = request.GET.getlist('content_types') or []
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

        # TODO
        fixed = False
        if fixed:
            image_results = _get_image_results(
                content_types, occurrence_result_ids, quote_result_ids, **search_kwargs
            )
            source_results, source_result_ids = _get_source_results(
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
            .order_by('key')
            .distinct()
        )

        ordered_queryset = self.order_queryset(
            # Combine querysets
            chain(
                occurrence_results, quote_results
            )  # , image_results)  # , source_results)
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


def _get_occurrence_results(content_types, **search_kwargs):
    if ModelNameSet.occurrence in content_types or not content_types:
        occurrence_results = list(Occurrence.objects.search(**search_kwargs).iterator())
    else:
        occurrence_results = []
    return occurrence_results, [
        occurrence.pk for occurrence in occurrence_results if occurrence
    ]


def _get_quote_results(content_types, occurrence_result_ids, **search_kwargs):
    if ModelNameSet.quote in content_types or not content_types:
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
    if ModelNameSet.image in content_types or not content_types:
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
    if ModelNameSet.source in content_types or not content_types:
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
