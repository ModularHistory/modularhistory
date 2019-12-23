from django.db import models
from tinymce.models import HTMLField

from occurrences.models import Year
from people.models import Person
from sources.models import Source


class Quote(models.Model):
    """A quote"""
    text = models.TextField(unique=True)
    context = HTMLField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    year = models.ManyToManyField(Year, related_name='quotes', blank=True)
    attributee = models.ForeignKey(Person, blank=True, null=True, related_name='locations', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.text} — {self.attributee}, {self.year or "date unknown"}'


class SourceReference(models.Model):
    """A reference to a source."""
    quote = models.ForeignKey(Quote, related_name='sources', on_delete=models.PROTECT)
    source = models.ForeignKey(Source, related_name='quote_references', on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(verbose_name='reference position')
    page_number = models.CharField(max_length=20)
    notes = models.TextField()
