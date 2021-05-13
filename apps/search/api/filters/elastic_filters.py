import logging
from pprint import pformat
from typing import List, Optional

from elasticsearch_dsl import Q
from rest_framework import filters

from apps.search.documents.config import get_index_name_for_ct

QUERY_PARAM = 'query'
START_YEAR_PARAM = 'start_year'
END_YEAR_PARAM = 'end_year'
ENTITIES_PARAM = 'entities'
QUALITY_PARAM = 'quality'
TOPICS_PARAM = 'topics'


class ModulesSearchFilterBackend(filters.BaseFilterBackend):
    """
    Main ES filter backend.
    TODO: this could be broken down to multiple filters if #apply_filter logic grows too big
    """

    def filter_queryset(self, request, queryset, view):
        filter_kwargs = self.get_filter_params(request)
        queryset = self.apply_filter(queryset, **filter_kwargs)

        return queryset

    @staticmethod
    def get_filter_params(request):
        indexes = '*'
        content_types = request.query_params.getlist('content_types') or None
        if content_types:
            indexes = ','.join(map(lambda c: get_index_name_for_ct(c), content_types))

        query_string = request.query_params.get(QUERY_PARAM, None)
        suppress_unverified = request.query_params.get(QUALITY_PARAM) == 'verified'

        start_year = request.query_params.get(START_YEAR_PARAM, None)
        end_year = request.query_params.get(END_YEAR_PARAM, None)

        entities = request.query_params.getlist(ENTITIES_PARAM, None)
        entity_ids = [int(entity_id) for entity_id in entities] if entities else None

        topics = request.query_params.getlist(TOPICS_PARAM, None)
        topic_ids = [int(topic_id) for topic_id in topics] if topics else None

        return {
            'indexes': indexes,
            'query_string': query_string,
            'start_year': start_year,
            'end_year': end_year,
            'entity_ids': entity_ids,
            'topic_ids': topic_ids,
            'suppress_unverified': suppress_unverified,
            'suppress_hidden': True,
        }

    @staticmethod
    def apply_filter(
        qs,
        indexes: str,
        query_string: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        entity_ids: Optional[List[int]] = None,
        topic_ids: Optional[List[int]] = None,
        suppress_unverified: bool = True,
        suppress_hidden: bool = True,
    ):

        qs = qs.index(indexes)

        # sorts by relevance, falls back to date sort when scores aren't available (i.e when there's no query)
        qs = qs.sort('_score', 'date')

        if query_string:
            query = Q('simple_query_string', query=query_string)
            qs = qs.query(query)

        if start_year or end_year:
            date_range = {}
            if start_year:
                date_range['gte'] = int(start_year)
            if end_year:
                date_range['lte'] = int(end_year)
            qs = qs.query('bool', filter=[Q('range', date_year=date_range)])

        if entity_ids:
            qs = qs.query(
                'bool',
                filter=[
                    Q('terms', involved_entities__id=entity_ids)
                    | Q('terms', attributees__id=entity_ids)
                ],
            )

        if topic_ids:
            qs = qs.query('bool', filter=[Q('terms', topics__id=topic_ids)])

        if suppress_unverified:
            qs = qs.query('bool', filter=[Q('match', verified=True)])

        if suppress_hidden:
            qs = qs.query('bool', filter=[Q('match', hidden=False)])

        # TODO: refactor & improve this. currently only applying highlights to quote#text and occurrence#description
        qs = qs.highlight(
            'text',
            number_of_fragments=1,
            type='plain',
            pre_tags=['<mark>'],
            post_tags=['</mark>'],
        )
        qs = qs.highlight(
            'description',
            number_of_fragments=1,
            type='plain',
            pre_tags=['<mark>'],
            post_tags=['</mark>'],
        )

        logging.info(f'ES Indexes: {indexes}')
        logging.info(f'ES Query: {pformat(qs.to_dict())}')

        return qs
