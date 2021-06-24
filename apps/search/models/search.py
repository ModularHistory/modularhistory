"""Models for the search app."""


from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.dates.fields import HistoricDateTimeField
from core.models.model import ExtendedModel

CONTENT_TYPE_OPTIONS: list[tuple[str, str]] = [
    ('propositions.occurrence', 'Occurrences'),
    ('quotes.quote', 'Quotes'),
    ('images.image', 'Images'),
    ('sources.source', 'Sources'),
]

ORDERING_OPTIONS = (('date', 'Date'), ('relevance', 'Relevance'))


class UserSearch(ExtendedModel):
    """An instance of a search by a user."""

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name='searches',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    search = models.ForeignKey(
        to='search.Search',
        related_name='user_searches',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the user–search instance."""
        return f'{self.user}, {self.datetime}, `{self.search}`'


class Search(ExtendedModel):
    """A search."""

    query = models.CharField(verbose_name=_('query'), max_length=100, null=True, blank=True)
    ordering = models.CharField(max_length=10, choices=ORDERING_OPTIONS)
    start_year = HistoricDateTimeField(null=True, blank=True)
    end_year = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for Search."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'Searches'

    def __str__(self) -> str:
        """Return a string representation of the search."""
        return str(self.query)
