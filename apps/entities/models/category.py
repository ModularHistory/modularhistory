"""Model classes for entity categories/categorizations."""

from typing import Tuple

from django.db import models
from django.db.models import CASCADE, ForeignKey
from django.db.models.functions import Lower

from modularhistory.fields import ArrayField, HistoricDateTimeField
from modularhistory.models import Model

NAME_MAX_LENGTH: int = 100

PARTS_OF_SPEECH: Tuple[Tuple[str, str], ...] = (
    ('noun', 'noun'),
    ('adj', 'adjective'),
    ('any', 'noun / adjective'),
)


class Category(Model):
    """An entity category."""

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    part_of_speech = models.CharField(
        max_length=9, choices=PARTS_OF_SPEECH, default='adj'
    )
    aliases = ArrayField(
        models.CharField(max_length=NAME_MAX_LENGTH), null=True, blank=True
    )
    parent = ForeignKey(
        'self', related_name='children', null=True, blank=True, on_delete=CASCADE
    )
    weight = models.PositiveSmallIntegerField(default=1, blank=True)

    class Meta:
        """
        Meta options for the Category model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        verbose_name_plural = 'categories'
        ordering = [Lower('name')]

    def __str__(self) -> str:
        """Return the category's string representation."""
        return self.name


class Categorization(Model):
    """A categorization of an entity."""

    entity = ForeignKey(
        'entities.Entity', related_name='categorizations', on_delete=CASCADE
    )
    category = ForeignKey(
        Category,
        related_name='categorizations',
        on_delete=CASCADE,
        null=True,
        blank=True,
    )
    date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        """
        Meta options for the Categorization model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        unique_together = ['entity', 'category']

    def __str__(self) -> str:
        """Return the categorization's string representation."""
        return str(self.category)

    @property
    def weight(self) -> int:
        """Return the categorization weight."""
        return self.category.weight
