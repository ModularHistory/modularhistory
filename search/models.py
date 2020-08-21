from django.db import models
from django.db.models import ForeignKey, SET_NULL, CASCADE
from typing import List, Tuple
from account.models import User
from history.fields import HistoricDateTimeField
from history.models import Model, DatedModel, SearchableMixin, PolymorphicModel


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
    ORDERING_CHOICES = (
        ('date', 'Date'),
        ('relevance', 'Relevance')
    )
    CONTENT_TYPES: List[Tuple[int, str]]

    query = models.CharField(max_length=100, null=True, blank=True)
    ordering = models.CharField(max_length=10, choices=ORDERING_CHOICES)
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
