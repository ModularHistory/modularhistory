"""Manager class for quotes."""
import random
from typing import List, Optional

from django.db.models import Q
from elasticsearch_dsl import Q as Q2

from apps.search.models.manager import SearchableModelManager, SearchableModelQuerySet
from core.constants.content_types import ContentTypes, get_ct_id


class QuoteManager(SearchableModelManager):
    """Manager for quotes."""

    def search(
        self,
        query: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        entity_ids: Optional[List[int]] = None,
        topic_ids: Optional[List[int]] = None,
        rank: bool = False,
        suppress_unverified: bool = True,
        suppress_hidden: bool = True,
    ) -> 'SearchableModelQuerySet':
        """Return search results from apps.quotes."""

        if not query:
            es_qs = super().search(suppress_unverified=suppress_unverified, suppress_hidden=suppress_hidden)
        else:
            es_query = Q2('simple_query_string', query=query)
            from apps.search.documents.quote import QuoteDocument
            es_qs = QuoteDocument.search().query(es_query)[0:10000]
            es_qs = es_qs.source(excludes=['*'])
            es_qs = es_qs.highlight('text', number_of_fragments=1, type='plain', pre_tags=['<mark>'], post_tags=['</mark>'])
            response = es_qs.execute()
            print(f"Query took: {response.took} ms, results n={response.hits.total.value}")

            for hit in response.hits:
                if hit.meta.id == '178':
                    print(f"Item: {hit}")
                    print(f"Item.meta: {hit.meta}")
                    if hasattr(hit.meta, 'highlight'):
                         print(f"Highlight: {hit.meta.highlight.text}")
            es_qs = es_qs.to_queryset(keep_order=False)

        qs = (
            es_qs
            .filter(hidden=False)
            .filter_by_date(start_year=start_year, end_year=end_year)
        )
        # Limit to specified entities
        if entity_ids:
            qs = qs.filter(
                Q(attributees__id__in=entity_ids)
                | Q(
                    relations__content_type_id=get_ct_id(ContentTypes.occurrence),
                    relations__object_id__in=entity_ids,
                )
            )
        # Limit to specified topics
        if topic_ids:
            qs = qs.filter(
                Q(tags__topic__id__in=topic_ids)
                | Q(tags__topic__related_topics__id__in=topic_ids)
            )
        return qs
