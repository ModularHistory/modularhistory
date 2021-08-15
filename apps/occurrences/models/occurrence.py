from typing import TYPE_CHECKING

from django.db import models

from apps.dates.models import DatedModel
from apps.propositions.api.serializers import OccurrenceSerializer
from apps.search.models import SearchableModel
from core.fields.html_field import PlaceholderGroups
from core.models.manager import SearchableManager
from core.utils.html import escape_quotes, soupify
from core.utils.string import dedupe_newlines, truncate

if TYPE_CHECKING:
    from django.db.models.query import QuerySet



class OccurrenceManager(SearchableManager):
    """Manager for occurrences."""

    def get_queryset(self) -> 'QuerySet[Occurrence]':
        return super().get_queryset().select_related('proposition')


class Occurrence(SearchableModel, DatedModel):
    """An occurrence, i.e., something that has happened."""

    # Each occurrence is proposed (with some degree of certainty) to have occurred.
    proposition = models.OneToOneField(
        to='propositions.Proposition',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='occurrence',
    )

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        ordering = ['date']

    objects = OccurrenceManager()
    serializer = OccurrenceSerializer

    def __str__(self) -> str:
        """Return the proposition's string representation."""
        return self.proposition.summary


class Birth(Occurrence):
    """A birth of an entity."""

    class Meta:
        proxy = True


class Death(Occurrence):
    """A death of an entity."""

    class Meta:
        proxy = True


class Publication(Occurrence):
    """A publication of a source."""

    class Meta:
        proxy = True


class Speech(Occurrence):
    """A speech."""

    class Meta:
        proxy = True
