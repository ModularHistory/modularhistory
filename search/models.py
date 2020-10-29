"""Models for the search app."""

from typing import List, Tuple

from django.db import models
from django.db.models import CASCADE, SET_NULL, ForeignKey

from account.models import User
from modularhistory.constants import CONTENT_TYPE_IDS
from modularhistory.fields import HistoricDateTimeField
from modularhistory.models import Model

CONTENT_TYPE_OPTIONS: List[Tuple[int, str]] = [
    (CONTENT_TYPE_IDS['occurrence'], 'Occurrences'),
    (CONTENT_TYPE_IDS['quote'], 'Quotes'),
    (CONTENT_TYPE_IDS['image'], 'Images'),
    (CONTENT_TYPE_IDS['source'], 'Sources'),
]

ORDERING_OPTIONS = (('date', 'Date'), ('relevance', 'Relevance'))


class UserSearch(Model):
    """An instance of a search by a user."""

    user = ForeignKey(
        User, related_name='searches', null=True, blank=True, on_delete=SET_NULL
    )
    search = ForeignKey(
        'search.Search',
        related_name='user_searches',
        null=False,
        blank=False,
        on_delete=CASCADE,
    )
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the user–search instance."""
        return f'{self.user}, {self.datetime}, `{self.search}`'


class Search(Model):
    """A search."""

    query = models.CharField(max_length=100, null=True, blank=True)
    ordering = models.CharField(max_length=10, choices=ORDERING_OPTIONS)
    start_year = HistoricDateTimeField(null=True, blank=True)
    end_year = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Searches'

    def __str__(self) -> str:
        """Return a string representation of the search."""
        return str(self.query)
