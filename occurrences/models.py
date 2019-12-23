from django.db import models
from tinymce.models import HTMLField

from sources.models import Source


class Occurrence(models.Model):
    """Something that happened"""
    summary = models.CharField(max_length=200)
    description = HTMLField(null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    # year = models.ManyToManyField('occurrences.Year', blank=True, related_name='occurrences')
    # location = models.ForeignKey('places.Location', null=True, related_name='occurrences', on_delete=models.PROTECT)
    # people = models.ManyToManyField(Person, blank=True)


class Year(models.Model):
    """A year in history"""
    ybp = models.BigIntegerField(verbose_name='Years Before Present', name='YBP', unique=True, blank=True, null=True)
    bce = models.BigIntegerField(verbose_name='Before Common Era', name='BCE', unique=True, blank=True, null=True)
    ce = models.PositiveSmallIntegerField(verbose_name='Common Era', name='CE', unique=True, blank=True, null=True)

    def __str__(self):
        return (f'{self.ce} CE' if self.ce
                else f'{self.bce} BCE' if self.bce
                else f'{self.ybp} YBP' if self.ybp
                else self)

    def get_ybp(self) -> str:
        return str(self.ybp) if self.ybp else 'tbd'

    @property
    def __str__(self):
        return f'{self.name}'


class SourceReference(models.Model):
    """A reference to a source."""
    occurrence = models.ForeignKey(Occurrence, related_name='sources', on_delete=models.PROTECT)
    source = models.ForeignKey(Source, related_name='occurrence_references', on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(verbose_name='reference position')
    page_number = models.CharField(max_length=20)
    notes = models.TextField()
