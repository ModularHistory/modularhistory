from datetime import date, datetime
from sys import stderr
from typing import Any, List, Optional, Union

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import (
    Model as BaseModel,
    Manager as BaseManager,
    # Q,
    QuerySet,
    BooleanField,
)
from django.utils.safestring import SafeText, mark_safe
from polymorphic.managers import PolymorphicManager as BasePolymorphicManager
from polymorphic.models import PolymorphicModel as BasePolymorphicModel
from polymorphic.query import PolymorphicQuerySet

from history.structures.historic_datetime import HistoricDateTime


# from typedmodels.models import TypedModel as BaseTypedModel


class Manager(BaseManager):
    def search(self, query=None) -> Union[QuerySet, PolymorphicQuerySet]:
        qs = self.get_queryset()
        if not query:
            return qs
        model = self.model
        searchable_fields = model.get_searchable_fields()
        if searchable_fields:
            # q = Q()
            # for attr in searchable_fields:
            #     q |= Q(**{f'{attr}__search': query})
            # qs = qs.filter(q).distinct()  # distinct() is often necessary with Q lookups
            query = SearchQuery(query)
            vector = SearchVector(*searchable_fields)
            ## https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/
            # rank = SearchRank(vector, query)
            # qs = qs.annotate(rank=rank).order_by('rank')
            qs = qs.annotate(search=vector).filter(search=query).order_by('id').distinct('id')
        return qs

    def get_closest_to_datetime(self, datetime_value: Union[date, datetime, HistoricDateTime],
                                datetime_attr: str = 'date'):
        qs = self.get_queryset()
        greater = qs.filter(date__gte=datetime_value).order_by(datetime_attr).first()
        lesser = qs.filter(date__lte=datetime_value).order_by(f'-{datetime_attr}').first()
        if not greater and not lesser:
            first_item = qs.first()
            print(f'No items with {datetime_attr} attribute; returning first item instead: {first_item}', file=stderr)
            return first_item
        elif greater and lesser:
            greater_diff = abs(getattr(greater, datetime_attr) - datetime_value)
            lesser_diff = abs(getattr(lesser, datetime_attr) - datetime_value)
            return greater if greater_diff < lesser_diff else lesser
        else:
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


class VerifiableMixin(BaseModel):
    verified = BooleanField(default=False)

    class Meta:
        abstract = True


class Model(BaseModel):
    objects: Manager = Manager()
    searchable_fields: Optional[List] = None

    @classmethod
    def get_searchable_fields(cls) -> List:
        return cls.searchable_fields or []

    class Meta:
        abstract = True


class PolymorphicManager(BasePolymorphicManager, Manager):
    pass


class PolymorphicModel(BasePolymorphicModel, Model):
    objects = PolymorphicManager()

    class Meta:
        abstract = True


class TypedModel(Model):
    objects: Any

    class Meta:
        abstract = True


class TaggableModel(Model):
    """Mixin for models that are topic-taggable."""
    related_topics = QuerySet

    class Meta:
        abstract = True

    @property
    def topic_tags(self) -> Optional[SafeText]:
        if self.related_topics and len(self.related_topics.all()):
            return mark_safe(' '.join([f'<li class="topic-tag"><a>{topic.key}</a></li>'
                                       for topic in self.related_topics.all()]))
        return None

