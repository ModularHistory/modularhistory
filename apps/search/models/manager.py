"""Manager classes for ModularHistory's models."""

from typing import Any, Dict, List, Optional

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import QuerySet

from modularhistory.models.manager import Manager


class SearchableModelQuerySet(QuerySet):
    """A queryset for a searchable model."""

    def filter_by_date(
        self,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> 'SearchableModelQuerySet':
        """Return a queryset filtered by start_year and/or end_year."""
        qs = self
        if start_year:
            qs = qs.filter(date__year__gte=start_year)
        if end_year:
            qs = qs.filter(date__year__lte=end_year)
        return qs

    def search(
        self, query: Optional[str] = None, rank: bool = False
    ) -> 'SearchableModelQuerySet':
        """Return search results from apps.occurrences."""
        qs: 'SearchableModelQuerySet' = self
        searchable_fields = qs.model.get_searchable_fields()
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
                for additional_vector in vectors[1:]:
                    vector += additional_vector
            annotations: Dict[str, Any] = {'search': vector}
            if rank:
                annotations['rank'] = SearchRank(vector, search_query)
            qs = qs.annotate(**annotations)  # type: ignore
            qs = qs.filter(search=search_query)
        distinct_results = qs.order_by('pk').distinct('pk')
        return distinct_results


class SearchableModelManager(Manager):
    """Manager for searchable models."""

    def get_queryset(self) -> SearchableModelQuerySet:
        """Override get_queryset to use SearchableModelQuerySet."""
        return SearchableModelQuerySet(self.model, using=self._db)

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
    ) -> SearchableModelQuerySet:
        """Return a queryset of search results."""
        qs = self.get_queryset().prefetch_related('tags__topic')
        if suppress_unverified:
            qs = qs.filter(verified=True)
        if suppress_hidden:
            qs = qs.filter(hidden=False)
        return qs.search(query=query, rank=rank)
