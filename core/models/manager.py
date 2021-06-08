"""Manager classes for ModularHistory's models."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Iterable, Optional, Sequence, Union

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Manager as ModelManager
from django.db.models import QuerySet
from django.utils.module_loading import import_string
from elasticsearch_dsl import Q
from typedmodels.models import TypedModelManager as BaseTypedModelManager

from apps.dates.structures import HistoricDateTime

if TYPE_CHECKING:
    from apps.search.documents.base import Document
    from core.models.model import Model

SearchResults = Union[QuerySet['Model'], Sequence['Model']]


class SearchableMixin:
    """Mixin for adding search capability to manager and queryset classes."""

    def get_closest_to_datetime(
        self,
        datetime_value: Union[date, datetime, HistoricDateTime],
        datetime_attr: str = 'date',
    ) -> 'Model':
        """Return the model instance closest to the specified datetime_value."""
        greater = self.filter(date__gte=datetime_value).order_by(datetime_attr).first()
        lesser = self.filter(date__lte=datetime_value).order_by(f'-{datetime_attr}').first()
        if not greater and not lesser:  # TODO
            return self.first()
        elif greater and lesser:
            greater_diff = abs(getattr(greater, datetime_attr) - datetime_value)
            lesser_diff = abs(getattr(lesser, datetime_attr) - datetime_value)
            return greater if greater_diff < lesser_diff else lesser
        return greater or lesser

    def search(self, term: str, fields: Iterable[str] = None) -> SearchResults:
        """Return search results."""
        searchable_fields = fields or getattr(self.model, 'searchable_fields', None)
        if searchable_fields and term:
            model_name = self.model.__name__
            index: Optional['Document']
            try:
                index = import_string(
                    f'apps.search.documents.{model_name.lower()}.{model_name}Document'
                )
            except ImportError as err:
                print(err)
                index = None
            if index:
                query = Q('simple_query_string', query=term)
                results: QuerySet = index.search().query(query).to_queryset()
                # If the calling object is a queryset (rather than a manager),
                # ensure the search results don't include model instances that
                # were already filtered out of the queryset.
                if isinstance(self, QuerySet):
                    base_ids = self.values_list('pk', flat=True)
                    results = results.filter(pk__in=base_ids)
            else:
                # Use Postgres full-text search.
                weights = ['A', 'B', 'C', 'D']
                vector = SearchVector(searchable_fields[0], weight=weights[0])
                for index, field in enumerate(searchable_fields[1:]):
                    try:
                        weight = weights[index + 1]
                    except IndexError:
                        weight = 'D'
                    vector += SearchVector(field, weight=weight)
                search_terms = term.split(' ')
                # https://www.postgresql.org/docs/current/functions-textsearch.html
                query = f'{" & ".join(search_terms)}:*'
                # Use subquery as a workaround to guarantee distinct results in queryset.
                guarantee_distinct_results = True
                search = SearchQuery(query, search_type='raw')
                if guarantee_distinct_results:
                    results = {
                        result.pk: result.rank
                        for result in self.annotate(rank=SearchRank(vector, search)).filter(
                            rank__gt=0
                        )
                    }
                    return sorted(
                        self.filter(pk__in=results.keys()),
                        key=lambda result: -results[result.pk],  # rank
                    )
                results = (
                    self.annotate(rank=SearchRank(vector, search))
                    .filter(rank__gt=0)
                    .order_by('-rank')
                )
        else:
            results = self.all()
        return results


class SearchableQuerySet(SearchableMixin, QuerySet):
    """A searchable queryset."""

    def get_by_natural_key(self, *args) -> 'Model':
        """Retrieve a model instance by its natural key."""
        fields = self.model.natural_key_fields
        natural_key = {}
        for index, field in enumerate(fields):
            natural_key[field] = args[index]
        return self.get(**natural_key)


class SearchableManager(SearchableMixin, ModelManager):
    """Base manager for ModularHistory's models."""

    def get_by_natural_key(self, *args) -> 'Model':
        """Retrieve a model instance by its natural key."""
        fields = self.model.natural_key_fields
        natural_key = {}
        for index, field in enumerate(fields):
            natural_key[field] = args[index]
        return self.get(**natural_key)


class TypedModelManager(BaseTypedModelManager, SearchableManager):
    """Wrapper for TypedModelManager."""
