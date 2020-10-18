"""Manager classes for ModularHistory's models."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Manager as ModelManager, QuerySet
from typedmodels.models import TypedModelManager as BaseTypedModelManager

from modularhistory.structures.historic_datetime import HistoricDateTime

if TYPE_CHECKING:
    from modularhistory.models import Model


class Manager(ModelManager):
    """Base manager for ModularHistory's models."""

    def get_by_natural_key(self, *args):
        """TODO: add docstring."""
        fields = self.model.natural_key_fields
        natural_key = {}
        for n, field in enumerate(fields):
            natural_key[field] = args[n]
        return self.get(**natural_key)

    def get_closest_to_datetime(
        self,
        datetime_value: Union[date, datetime, HistoricDateTime],
        datetime_attr: str = 'date'
    ) -> 'Model':
        """TODO: add docstring."""
        qs = self.get_queryset()
        greater = qs.filter(date__gte=datetime_value).order_by(datetime_attr).first()
        lesser = qs.filter(date__lte=datetime_value).order_by(f'-{datetime_attr}').first()
        if not greater and not lesser:  # TODO
            return qs.first()
        elif greater and lesser:
            greater_diff = abs(getattr(greater, datetime_attr) - datetime_value)
            lesser_diff = abs(getattr(lesser, datetime_attr) - datetime_value)
            return greater if greater_diff < lesser_diff else lesser
        return greater or lesser

    # def with_counts(self):
    #     from django.db import connection
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT p.id, p.question, p.poll_date, COUNT(*)
    #             FROM polls_opinionpoll p, polls_response r
    #             WHERE p.id = r.poll_id
    #             GROUP BY p.id, p.question, p.poll_date
    #             ORDER BY p.poll_date DESC""")
    #         result_list = []
    #         for row in cursor.fetchall():
    #             p = self.model(id=row[0], question=row[1], poll_date=row[2])
    #             p.num_responses = row[3]
    #             result_list.append(p)
    #     return result_list


class SearchableModelQuerySet(QuerySet):
    """A queryset for a searchable model."""

    def filter_by_date(
        self,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> 'SearchableModelQuerySet':
        """Returns a queryset filtered by start_year and/or end_year."""
        qs = self
        if start_year:
            qs = qs.filter(date__year__gte=start_year)
        if end_year:
            qs = qs.filter(date__year__lte=end_year)
        return qs

    def search(
        self,
        query: Optional[str] = None,
        rank: bool = False
    ) -> 'SearchableModelQuerySet':
        """Returns search results from occurrences."""
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
                for v in vectors[1:]:
                    vector += v
            annotations: Dict[str, Any] = {'search': vector}
            if rank:
                annotations['rank'] = SearchRank(vector, search_query)
            qs = qs.annotate(**annotations).filter(search=search_query)  # type: ignore
        return qs.order_by('id').distinct('id')


class SearchableModelManager(Manager):
    """Manager for searchable models."""

    def get_queryset(self) -> SearchableModelQuerySet:
        """Overrides get_queryset to use SearchableModelQuerySet."""
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
        db: str = 'default'
    ) -> SearchableModelQuerySet:
        """Returns a queryset of search results."""
        qs = self.get_queryset()
        if suppress_unverified:
            qs = qs.filter(verified=True)
        return qs.search(query=query, rank=rank)


class TypedModelManager(BaseTypedModelManager, Manager):
    """Wrapper for TypedModelManager."""

    pass
