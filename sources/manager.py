from typing import Any, Dict, List, Optional

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import QuerySet, Q

from history.models import TypedModelManager  # , PolymorphicManager


class SourceManager(TypedModelManager):
    """Manager for sources."""

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
                Q(attributees__id__in=entity_ids)
            )

        searchable_fields = self.model.get_searchable_fields()
        if query and searchable_fields:
            search_query = SearchQuery(query)
            # https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/#weighting-queries
            vectors = []
            for searchable_field in searchable_fields:
                if isinstance(searchable_field, (tuple, list)):
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
