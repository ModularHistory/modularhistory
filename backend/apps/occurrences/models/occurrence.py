from typing import TYPE_CHECKING

from django.db import models
from rest_framework.serializers import Serializer

from apps.dates.models import DatedModel
from core.models.module import Module, ModuleManager

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class OccurrenceManager(ModuleManager):
    """Manager for occurrences."""

    def get_queryset(self) -> 'QuerySet[Occurrence]':
        return super().get_queryset().select_related('proposition')


class Occurrence(Module, DatedModel):
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

    @classmethod
    def get_serializer(self) -> type[Serializer]:
        """Return the serializer for the entity."""
        from apps.propositions.api.serializers import OccurrenceSerializer

        return OccurrenceSerializer

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
