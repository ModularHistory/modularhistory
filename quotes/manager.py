"""Manager class for quotes."""

from typing import Any, Dict, List, Optional

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Q, QuerySet  # , Subquery

from modularhistory.constants import OCCURRENCE_CT_ID
from modularhistory.models import Manager as BaseManager


class QuoteManager(BaseManager):
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
        db: str = 'default'
    ) -> QuerySet:
        """TODO: add docstring."""
        qs = super().search(db=db, suppress_unverified=suppress_unverified).filter(hidden=False)

        # Limit to specified date range
        if start_year:
            qs = qs.filter(date__year__gte=start_year)
        if end_year:
            qs = qs.filter(date__year__lte=end_year)

        # Limit to specified entities
        if entity_ids:
            qs = qs.filter(
                Q(attributees__id__in=entity_ids) |
                # Q(related_occurrences__involved_entities__id__in=entity_ids)
                Q(
                    relations__content_type_id=OCCURRENCE_CT_ID,
                    relations__object_id__in=entity_ids
                )
            )

        # Limit to specified topics
        if topic_ids:
            qs = qs.filter(
                Q(tags__topic__id__in=topic_ids) |
                Q(tags__topic__related_topics__id__in=topic_ids)
            )

        searchable_fields = self.model.get_searchable_fields()
        if query and searchable_fields:
            search_query = SearchQuery(query)
            # https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/#weighting-queries
            vectors = []
            for searchable_field in searchable_fields:
                if isinstance(searchable_field, (list, tuple)):
                    field, weight = searchable_field
                    vectors.append(SearchVector(field, weight=weight))
                else:
                    vectors.append(SearchVector(searchable_field))
            vector: SearchVector = vectors[0]
            if len(vectors) > 1:
                for v in vectors[1:]:
                    vector += v
            annotations: Dict[str, Any] = {'search': vector}
            if rank:
                annotations['rank'] = SearchRank(vector, search_query)
            qs = qs.annotate(**annotations).filter(search=search_query)
        return qs.order_by('id').distinct('id')
