from django.db import models
from django.db.models import CASCADE
from django.utils.safestring import SafeText, mark_safe

from history.models import Model

importance_options = (
    (1, 'Primary'),
    (2, 'Secondary'),
    (3, 'Tertiary'),
    (4, 'Quaternary'),
    (5, 'Quinary'),
    (6, 'Senary'),
    (7, 'Septenary'),
)


class OccurrenceLocation(Model):
    """A place being a site of an occurrence"""
    occurrence = models.ForeignKey('occurrences.Occurrence', on_delete=CASCADE)
    location = models.ForeignKey(
        'places.Place',
        related_name='location_occurrences',
        on_delete=CASCADE
    )
    importance = models.IntegerField(choices=importance_options, default=1)

    class Meta:
        unique_together = ['occurrence', 'location']


class OccurrenceEntityInvolvement(Model):
    """An involvement of an entity in an occurrence"""
    occurrence = models.ForeignKey('occurrences.Occurrence', on_delete=CASCADE)
    entity = models.ForeignKey(
        'entities.Entity',
        related_name='occurrence_involvements',
        on_delete=CASCADE
    )
    importance = models.PositiveSmallIntegerField(choices=importance_options, default=1)

    class Meta:
        unique_together = ['occurrence', 'entity']

    def __str__(self) -> SafeText:
        return mark_safe(f'{self.occurrence.date_string}: {self.occurrence.summary}')


class OccurrenceQuoteRelation(Model):
    """An involvement of an entity in an occurrence"""
    occurrence = models.ForeignKey(
        'occurrences.Occurrence',
        related_name='occurrence_quote_relations',
        on_delete=CASCADE
    )
    quote = models.ForeignKey(
        'quotes.Quote',
        related_name='quote_occurrence_relations',
        on_delete=CASCADE
    )
    position = models.PositiveSmallIntegerField(null=True, blank=True)  # TODO: add cleaning logic

    class Meta:
        unique_together = ['occurrence', 'quote']
        ordering = ['position', 'quote']

    def __str__(self):
        return mark_safe(f'{self.quote.citation}')

    @property
    def quote_pk(self) -> str:
        return self.quote.pk
