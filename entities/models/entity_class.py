# type: ignore
# TODO: remove above line after fixing typechecking
from django.db import models
from django.db.models import ForeignKey, CASCADE, SET_NULL

from history.fields import ArrayField, HistoricDateTimeField
from history.models import Model

parts_of_speech = (
    ('noun', 'noun'),
    ('adj', 'adjective'),
    ('any', 'noun / adjective'),
)


class Category(Model):
    """TODO: add docstring."""

    NAME_MAX_LENGTH: int = 100

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    part_of_speech = models.CharField(
        max_length=9, choices=parts_of_speech,
        default='adj'
    )
    aliases = ArrayField(
        models.CharField(max_length=NAME_MAX_LENGTH),
        null=True, blank=True
    )
    parent = ForeignKey(
        'self', related_name='children',
        null=True, blank=True,
        on_delete=CASCADE
    )
    weight = models.PositiveSmallIntegerField(default=1, blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.name


class Categorization(Model):
    """TODO: add docstring."""

    entity = ForeignKey(
        'entities.Entity',
        related_name='categorizations',
        on_delete=CASCADE
    )
    category = ForeignKey(
        Category,
        related_name='categorizations',
        on_delete=CASCADE,
        null=True, blank=True
    )
    date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['entity', 'category']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return str(self.category)

    @property
    def weight(self) -> int:
        """TODO: add docstring."""
        return self.category.weight


class Classification(Model):
    """TODO: add docstring."""

    NAME_MAX_LENGTH: int = 100

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    part_of_speech = models.CharField(
        max_length=9, choices=parts_of_speech,
        default='adj'
    )
    aliases = ArrayField(
        models.CharField(max_length=NAME_MAX_LENGTH),
        null=True, blank=True
    )
    parent = ForeignKey(
        'self', related_name='children',
        null=True, blank=True,
        on_delete=CASCADE
    )
    weight = models.PositiveSmallIntegerField(default=1, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.name


class EntityClassification(Model):
    """TODO: add docstring."""

    entity = ForeignKey(
        'entities.Entity',
        related_name='entity_classifications',
        on_delete=CASCADE
    )
    classification = ForeignKey(
        Classification,
        related_name='entity_classifications',
        on_delete=SET_NULL,
        null=True, blank=True
    )
    date = HistoricDateTimeField(null=True, blank=True)
    end_date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['entity', 'classification']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return str(self.classification)

    @property
    def weight(self) -> int:
        """TODO: add docstring."""
        return self.classification.weight
