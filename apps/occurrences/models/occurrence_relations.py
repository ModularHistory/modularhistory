from django.db import models
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from core.models.model import Model
from core.models.positioned_relation import PositionedRelation

IMPORTANCE_OPTIONS = (
    (1, 'Primary'),
    (2, 'Secondary'),
    (3, 'Tertiary'),
    (4, 'Quaternary'),
    (5, 'Quinary'),
    (6, 'Senary'),
    (7, 'Septenary'),
)


class OccurrenceLocation(Model):
    """A place being a site of an occurrence."""

    occurrence = models.ForeignKey(
        to='occurrences.Occurrence', on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        to='places.Place', related_name='location_occurrences', on_delete=models.CASCADE
    )
    importance = models.IntegerField(choices=IMPORTANCE_OPTIONS, default=1)

    class Meta:
        """Meta options for OccurrenceLocation."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        unique_together = ['occurrence', 'location']

    def __str__(self):
        """Return the string representation of the occurrence–location association."""
        return f'{self.location} : {self.occurrence}'


class OccurrenceQuoteRelation(PositionedRelation):
    """An involvement of an entity in an occurrence."""

    occurrence = models.ForeignKey(
        to='occurrences.Occurrence',
        related_name='occurrence_quote_relations',
        on_delete=models.CASCADE,
        verbose_name=_('occurrence'),
    )
    quote = models.ForeignKey(
        to='quotes.Quote',
        related_name='quote_occurrence_relations',
        on_delete=models.CASCADE,
        verbose_name=_('quote'),
    )

    class Meta:
        """Meta options for OccurrenceQuoteRelation."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        unique_together = ['occurrence', 'quote']
        ordering = ['position', 'quote']

    def __str__(self) -> str:
        """Return the string representation of the occurrence quote relation."""
        return format_html(f'{self.quote.citation}')

    @property
    def quote_pk(self) -> str:
        """TODO: write docstring."""
        return self.quote.pk


class OccurrenceEntityInvolvement(Model):
    """An involvement of an entity in an occurrence."""

    occurrence = models.ForeignKey(
        to='occurrences.Occurrence', on_delete=models.CASCADE
    )
    entity = models.ForeignKey(
        'entities.Entity',
        related_name='occurrence_involvements',
        on_delete=models.CASCADE,
    )
    importance = models.PositiveSmallIntegerField(choices=IMPORTANCE_OPTIONS, default=1)

    class Meta:
        """Meta options for OccurrenceEntityInvolvement."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        unique_together = ['occurrence', 'entity']

    def __str__(self) -> str:
        """Return the string representation of the occurrence entity involvement."""
        return format_html(f'{self.occurrence.date_string}: {self.occurrence.summary}')
