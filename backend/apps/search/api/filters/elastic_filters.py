from typing import Optional

from elasticsearch_dsl import Q
from rest_framework import filters

from apps.admin.widgets.historic_date_widget import CE
from apps.admin.widgets.historic_date_widget import (
    _datetime_from_datadict_values as historicdate_from_year,
)
from apps.dates.structures import HistoricDateTime

QUERY_PARAM = 'query'
START_YEAR_PARAM = 'start_year'
START_YEAR_TYPE_PARAM = 'start_year_type'
END_YEAR_PARAM = 'end_year'
END_YEAR_TYPE_PARAM = 'end_year_type'
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
            # #ContentTypesHardCoded
            allowed_content_types = {'occurrences', 'quotes', 'images', 'sources', 'entities'}
            indexes = ','.join(ct for ct in content_types if ct in allowed_content_types)
        # Temporarily exclude images.  TODO: Figure out what to do with images.
        # Note: The search filter form starts with the images content type unselected.
        else:
            indexes = 'occurrences,quotes,sources,entities'

        query_string = request.query_params.get(QUERY_PARAM, None)
        suppress_unverified = request.query_params.get(QUALITY_PARAM) == 'verified'

        start_year = request.query_params.get(START_YEAR_PARAM, None)
        end_year = request.query_params.get(END_YEAR_PARAM, None)
        start_year_type = request.query_params.get(START_YEAR_TYPE_PARAM, CE)
        end_year_type = request.query_params.get(END_YEAR_TYPE_PARAM, CE)

        start_date = (
            historicdate_from_year(start_year, start_year_type) if start_year else None
        )
        end_date = historicdate_from_year(end_year, end_year_type) if end_year else None

        entities = request.query_params.getlist(ENTITIES_PARAM, None)
        entity_ids = [int(entity_id) for entity_id in entities] if entities else None

        topics = request.query_params.getlist(TOPICS_PARAM, None)
        topic_ids = [int(topic_id) for topic_id in topics] if topics else None

        return {
            'indexes': indexes,
            'query_string': query_string,
            'start_date': start_date,
            'end_date': end_date,
            'entity_ids': entity_ids,
            'topic_ids': topic_ids,
            'suppress_unverified': suppress_unverified,
        }

    @staticmethod
    def apply_filter(
        qs,
        indexes: str,
        query_string: Optional[str] = None,
        start_date: Optional[HistoricDateTime] = None,
        end_date: Optional[HistoricDateTime] = None,
        entity_ids: Optional[list[int]] = None,
        topic_ids: Optional[list[int]] = None,
        suppress_unverified: bool = True,
    ):

        qs = qs.index(indexes)

        # sorts by relevance, falls back to date sort when scores aren't available (i.e when there's no query)
        qs = qs.sort('_score', 'date')

        if query_string:
            query = Q('simple_query_string', query=query_string)
            qs = qs.query(query)

        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range['gte'] = start_date
            if end_date:
                date_range['lte'] = end_date
            qs = qs.query('bool', filter=[Q('range', date=date_range)])

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
        qs = qs.highlight(
            'elaboration',
            number_of_fragments=1,
            type='plain',
            pre_tags=['<mark>'],
            post_tags=['</mark>'],
        )
        # logging.info(f'ES Indexes: {indexes}')
        # logging.info(f'ES Query: {pformat(qs.to_dict())}')
        return qs
