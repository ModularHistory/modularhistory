from typing import TYPE_CHECKING

from rest_framework.serializers import Serializer

from apps.propositions.models.proposition import Proposition
from core.models.manager import SearchableManager

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class OccurrenceManager(SearchableManager):
    """Manager for occurrences."""

    type_filter = 'propositions.occurrence'

    def __init__(self, type_filter: str = 'propositions.occurrence'):
        self.type_filter = type_filter
        super().__init__()

    def get_queryset(self) -> 'QuerySet[Occurrence]':
        """Return the propositions of type `propositions.occurrence`."""
        return super().get_queryset().filter(type=self.type_filter)


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

    @classmethod
    def get_serializer(self) -> type[Serializer]:
        """Return the serializer for the entity."""
        from apps.propositions.api.serializers import OccurrenceSerializer

        return OccurrenceSerializer


class Birth(Occurrence):
    """A birth of an entity."""

    objects = OccurrenceManager('propositions.birth')

    class Meta:
        proxy = True


class Death(Occurrence):
    """A death of an entity."""

    objects = OccurrenceManager('propositions.death')

    class Meta:
        proxy = True


class Publication(Occurrence):
    """A publication of a source."""

    objects = OccurrenceManager('propositions.publication')

    class Meta:
        proxy = True


class Speech(Occurrence):
    """A speech."""

    objects = OccurrenceManager('speech')

    class Meta:
        proxy = True
