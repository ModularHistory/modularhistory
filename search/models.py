from typing import List, Tuple

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import ForeignKey, SET_NULL, CASCADE

from account.models import User
from history.fields import HistoricDateTimeField
from history.models import Model, DatedModel, SearchableMixin, PolymorphicModel
from images.models import Image
from occurrences.models import Occurrence
from quotes.models import Quote
from sources.models import Source


class UserSearch(Model):
    """An instance of a search by a user."""
    user = ForeignKey(
        User, related_name='searches',
        null=True, blank=True, on_delete=SET_NULL
    )
    search = ForeignKey(
        'search.Search', related_name='user_searches',
        null=False, blank=False, on_delete=CASCADE
    )
    datetime = models.DateTimeField(auto_now_add=True)


class Search(Model):
    """A search."""
    ORDERING_OPTIONS = (
        ('date', 'Date'),
        ('relevance', 'Relevance')
    )
    CONTENT_TYPE_OPTIONS: List[Tuple[int, str]]

    query = models.CharField(max_length=100, null=True, blank=True)
    ordering = models.CharField(max_length=10, choices=ORDERING_OPTIONS)
    start_year = HistoricDateTimeField(null=True, blank=True)
    end_year = HistoricDateTimeField(null=True, blank=True)
    # entities = ManyToManyField(
    #
    # )  # TODO
    # topics = ManyToManyField(  # TODO
    # content_types =  # TODO

    class Meta:
        verbose_name_plural = 'Searches'

    def __str__(self):
        return str(self.query)

    @classmethod
    def get_content_type_options(cls):
        content_type_options = getattr(cls, 'CONTENT_TYPE_OPTIONS', None)
        if not content_type_options:
            cls.CONTENT_TYPE_OPTIONS = [
                (ContentType.objects.get_for_model(Occurrence).id, 'Occurrences'),
                (ContentType.objects.get_for_model(Quote).id, 'Quotes'),
                (ContentType.objects.get_for_model(Image).id, 'Images'),
                (ContentType.objects.get_for_model(Source).id, 'Sources')
            ]
        return cls.CONTENT_TYPE_OPTIONS
