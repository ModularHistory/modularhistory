"""Model classes for entity categories/categorizations."""


from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import ugettext_lazy as _

from apps.dates.fields import HistoricDateTimeField
from apps.moderation.models.moderated_model.model import ModeratedModel
from core.fields.array_field import ArrayField
from core.models.relations.moderated import ModeratedRelation

NAME_MAX_LENGTH: int = 100

PARTS_OF_SPEECH: tuple[tuple[str, str], ...] = (
    ('noun', 'noun'),
    ('adj', 'adjective'),
    ('any', 'noun / adjective'),
)


class Category(ModeratedModel):
    """An entity category."""

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    part_of_speech = models.CharField(
        verbose_name=_('part of speech'),
        max_length=9,
        choices=PARTS_OF_SPEECH,
        default='adj',
    )
    aliases = ArrayField(
        models.CharField(max_length=NAME_MAX_LENGTH),
        verbose_name=_('aliases'),
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        to='self',
        related_name='children',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    weight = models.PositiveSmallIntegerField(default=1, blank=True)

    class Meta:
        """Meta options for the Category model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'categories'
        ordering = [Lower('name')]

    def __str__(self) -> str:
        """Return the category's string representation."""
        return self.name


class Categorization(ModeratedRelation):
    """A categorization of an entity."""

    entity = models.ForeignKey(
        to='entities.Entity',
        related_name='categorizations',
        on_delete=models.CASCADE,
        verbose_name=_('entity'),
    )
    category = models.ForeignKey(
        to=Category,
        related_name='categorizations',
        on_delete=models.CASCADE,
        verbose_name=_('category'),
    )
    date = HistoricDateTimeField(verbose_name=_('date'), null=True, blank=True)
    end_date = HistoricDateTimeField(verbose_name=_('end date'), null=True, blank=True)

    class Meta:
        """Meta options for the Categorization model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        unique_together = ['entity', 'category']

    def __str__(self) -> str:
        """Return the categorization's string representation."""
        return str(self.category)

    @property
    def weight(self) -> int:
        """Return the categorization weight."""
        return self.category.weight
