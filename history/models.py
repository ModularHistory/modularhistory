import uuid
from datetime import date, datetime
from sys import stderr
from typing import Any, List, Optional, Union

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import (
    Model as BaseModel,
    Manager as BaseManager,
    # Q,
    QuerySet,
    BooleanField,
    UUIDField
)
from django.urls import reverse
from django.utils.safestring import SafeText, mark_safe
from polymorphic.managers import PolymorphicManager as BasePolymorphicManager
from polymorphic.models import PolymorphicModel as BasePolymorphicModel
from polymorphic.query import PolymorphicQuerySet

from history.fields.historic_datetime_field import HistoricDateTimeField
from history.structures.historic_datetime import HistoricDateTime


# from typedmodels.models import TypedModel as BaseTypedModel


class Manager(BaseManager):
    """Base manager for models."""
    def search(
            self,
            query: Optional[str] = None,
            start_year: Optional[int] = None,
            end_year: Optional[int] = None,
            entity_ids: Optional[List[int]] = None,
            topic_ids: Optional[List[int]] = None,
            rank: bool = False,
            suppress_unverified: bool = True
    ) -> Union[QuerySet, PolymorphicQuerySet]:
        qs = self.get_queryset().filter(hidden=False)
        searchable_fields = self.model.get_searchable_fields()
        if searchable_fields:
            # q = Q()
            # for attr in searchable_fields:
            #     q |= Q(**{f'{attr}__search': query})
            # qs = qs.filter(q).distinct()  # distinct() is often necessary with Q lookups

            query = SearchQuery(query)
            #  https://www.postgresql.org/docs/current/textsearch-controls.html#TEXTSEARCH-PARSING-QUERIES
            #  SearchQuery('red tomato', search_type='phrase')
            #  SearchQuery('"tomato" & ("red" | "green")', search_type='raw')
            #  SearchQuery('meat') & SearchQuery('cheese')  # AND
            #  SearchQuery('meat') | SearchQuery('cheese')  # OR
            #  ~SearchQuery('meat')  # NOT

            # https://docs.djangoproject.com/en/3.0/ref/contrib/postgres/search/#weighting-queries
            vectors = []
            for searchable_field in searchable_fields:
                if isinstance(searchable_field, tuple) or isinstance(searchable_field, list):
                    field, weight = searchable_field
                    vectors.append(SearchVector(field, weight=weight))
                else:
                    vectors.append(SearchVector(searchable_field))
            vector = vectors[0]
            if len(vectors) > 1:
                for v in vectors[1:]:
                    vector += v
            annotations = {'search': vector}
            if rank:
                annotations['rank'] = SearchRank(vector, query)
            qs = qs.annotate(**annotations).filter(
                search=query, hidden=False
            ).order_by('id').distinct('id')
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


class SearchableMixin(BaseModel):
    verified = BooleanField(default=False, blank=True)
    hidden = BooleanField(default=False, blank=True, help_text="Don't let this item appear in search results.")
    key = UUIDField(primary_key=False, default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True


class Model(BaseModel):
    objects: Manager = Manager()
    searchable_fields: Optional[List] = None

    @classmethod
    def get_searchable_fields(cls) -> List:
        return cls.searchable_fields or []

    @property
    def ctype(self) -> ContentType:
        return ContentType.objects.get_for_model(self)
    #
    # @property
    # def type(self) -> str:
    #     return self.ctype.name

    def get_admin_url(self):
        return reverse(f'admin:{self._meta.app_label}_{self._meta.model_name}_change', args=[self.id])

    class Meta:
        abstract = True


class PolymorphicManager(BasePolymorphicManager, Manager):
    pass


class PolymorphicModel(BasePolymorphicModel, Model):
    objects = PolymorphicManager()

    class Meta:
        abstract = True

    @property
    def ctype(self) -> ContentType:
        return self.polymorphic_ctype

    def get_admin_url(self):
        return reverse(f'admin:{self.ctype.app_label}_{self.ctype.model}_change', args=[self.id])


class TypedModel(Model):
    objects: Any

    class Meta:
        abstract = True


class DatedModel(Model):
    date_is_circa = BooleanField(blank=True, default=False)
    date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def _date_string(self) -> str:
        date_string = self.date.string if self.date else ''
        if date_string and self.date_is_circa and not date_string.startswith('c. '):
            date_string = f'c. {date_string}'
        if hasattr(self, 'end_date') and self.end_date:
            date_string = f'{date_string} – {self.end_date.string}'
        return date_string
    _date_string.admin_order_field = 'date'
    date_string = property(_date_string)

    @property
    def date_html(self) -> Optional[SafeText]:
        if not self.date:
            return None
        date_html = self.date.html
        if date_html and self.date_is_circa and not date_html.startswith('c. '):
            date_html = f'c. {date_html}'
        if hasattr(self, 'end_date') and self.end_date:
            date_html = f'{date_html} – {self.end_date.html}'
        if self.date.year < 1000 and not self.date.is_bce and not date_html.endswith(' CE'):
            date_html += ' CE'
        return mark_safe(date_html)


class TaggableModel(Model):
    """Mixin for models that are topic-taggable."""
    related_topics: QuerySet

    class Meta:
        abstract = True

    @property
    def topic_tags(self) -> Optional[SafeText]:
        if self.related_topics and len(self.related_topics.all()):
            return mark_safe(' '.join([f'<li class="topic-tag"><a>{topic.key}</a></li>'
                                       for topic in self.related_topics.all()]))
        return None

