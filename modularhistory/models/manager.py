"""Manager classes for ModularHistory's models."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Manager as ModelManager, QuerySet
from typedmodels.models import TypedModelManager as BaseTypedModelManager
import logging
from modularhistory.structures.historic_datetime import HistoricDateTime

if TYPE_CHECKING:
    from modularhistory.models import Model


class Manager(ModelManager):
    """Base manager for ModularHistory's models."""

    def get_by_natural_key(self, *args):
        """Retrieva model instance by its natural key."""
        fields = self.model.natural_key_fields
        natural_key = {}
        for index, field in enumerate(fields):
            natural_key[field] = args[index]
        return self.get(**natural_key)

    def get_closest_to_datetime(
        self,
        datetime_value: Union[date, datetime, HistoricDateTime],
        datetime_attr: str = 'date',
    ) -> 'Model':
        """Return the model instance closest to the specified datetime_value."""
        qs = self.get_queryset()
        greater = qs.filter(date__gte=datetime_value).order_by(datetime_attr).first()
        lesser = (
            qs.filter(date__lte=datetime_value).order_by(f'-{datetime_attr}').first()
        )
        if not greater and not lesser:  # TODO
            return qs.first()
        elif greater and lesser:
            greater_diff = abs(getattr(greater, datetime_attr) - datetime_value)
            lesser_diff = abs(getattr(lesser, datetime_attr) - datetime_value)
            return greater if greater_diff < lesser_diff else lesser
        return greater or lesser


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
        """Return search results from occurrences."""
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
        logging.info(f'Returning {len(distinct_results)} distinct search results...')
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


class TypedModelManager(BaseTypedModelManager, Manager):
    """Wrapper for TypedModelManager."""

    pass  # noqa: WPS604
