"""Manager classes for ModularHistory's models."""

from datetime import date, datetime
from typing import List, Optional, Union

# from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Manager as ModelManager, QuerySet
from typedmodels.models import TypedModelManager as BaseTypedModelManager

from modularhistory.structures.historic_datetime import HistoricDateTime


class Manager(ModelManager):
    """Base manager for ModularHistory's models."""

    def get_by_natural_key(self, *args):
        """TODO: add docstring."""
        fields = self.model.natural_key_fields
        natural_key = {}
        for n, field in enumerate(fields):
            natural_key[field] = args[n]
        return self.get(**natural_key)

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
        qs = self._queryset_class(model=self.model, using=db, hints=self._hints)
        if suppress_unverified:
            qs = qs.filter(verified=True)
        return qs

        # qs = self._queryset_class(
        #     model=self.model, using=db, hints=self._hints
        # ).filter(hidden=False)
        #
        # searchable_fields = self.model.get_searchable_fields()
        # if searchable_fields:
        #     # q = Q()
        #     # for attr in searchable_fields:
        #     #     q |= Q(**{f'{attr}__search': query})
        #     # qs = qs.filter(q).distinct()  # distinct() is often necessary with Q lookups
        #
        #     query = SearchQuery(query)
        #     #  https://www.postgresql.org/docs/current/textsearch-controls.html#TEXTSEARCH-PARSING-QUERIES
        #     #  SearchQuery('red tomato', search_type='phrase')
        #     #  SearchQuery('"tomato" & ("red" | "green")', search_type='raw')
        #     #  SearchQuery('meat') & SearchQuery('cheese')  # AND
        #     #  SearchQuery('meat') | SearchQuery('cheese')  # OR
        #     #  ~SearchQuery('meat')  # NOT
        #
        #     # https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/#weighting-queries
        #     vectors = []
        #     for searchable_field in searchable_fields:
        #         if isinstance(searchable_field, tuple) or isinstance(searchable_field, list):
        #             field, weight = searchable_field
        #             vectors.append(SearchVector(field, weight=weight))
        #         else:
        #             vectors.append(SearchVector(searchable_field))
        #     vector = vectors[0]
        #     if len(vectors) > 1:
        #         for v in vectors[1:]:
        #             vector += v
        #     annotations = {'search': vector}
        #     if rank:
        #         annotations['rank'] = SearchRank(vector, query)
        #     qs = qs.annotate(**annotations).filter(
        #         search=query, hidden=False
        #     ).order_by('id').distinct('id')
        # return qs

    def get_closest_to_datetime(
        self,
        datetime_value: Union[date, datetime, HistoricDateTime],
        datetime_attr: str = 'date'
    ):
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


class TypedModelManager(BaseTypedModelManager, Manager):
    """Wrapper for TypedModelManager."""

    pass


# class PolymorphicManager(BasePolymorphicManager, Manager):
#     """Wrapper for PolymorphicManager."""
#
#     pass
