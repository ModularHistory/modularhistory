from typing import TYPE_CHECKING

from apps.propositions.models.proposition import Proposition
from apps.propositions.serializers import OccurrenceSerializer
from core.models.manager import SearchableManager

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class OccurrenceManager(SearchableManager):
    """Manager for occurrences."""

    def get_queryset(self) -> 'QuerySet[Occurrence]':
        """Return the propositions of type `propositions.occurrence`."""
        return super().get_queryset().filter(type='propositions.occurrence')


class Occurrence(Proposition):
    """
    An occurrence, i.e., something that has happened.

    For our purposes, an occurrence is a proposition: each occurrence is proposed
    (with some degree of certainty) to have occurred. As such, this model inherits
    from `Proposition`.
    """

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        """Meta options for the `Occurrence` model."""

        proxy = True
        ordering = ['date']

    objects = OccurrenceManager()
    serializer = OccurrenceSerializer


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
