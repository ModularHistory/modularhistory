from typing import List, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import models
from taggit.models import TaggedItemBase

from entities.models import Entity
from history.fields import HTMLField, HistoricDateField
from history.models import Model, TaggableModel
from occurrences.models import Year
from sources.models import Source, SourceReference
from images.models import Image


class QuoteTag(TaggedItemBase):
    """An occurrence tag"""
    content_object = models.ForeignKey('Quote', on_delete=models.CASCADE)


class QuoteSourceReference(SourceReference):
    """A reference to a source."""
    quote = models.ForeignKey('Quote', related_name='source_references', on_delete=models.CASCADE)
    source = models.ForeignKey(Source, related_name='references_from_quotes', on_delete=models.CASCADE)


class Quote(TaggableModel):
    """A quote"""
    text = HTMLField()
    bite = HTMLField(null=True, blank=True)
    context = HTMLField(null=True, blank=True)
    date = HistoricDateField(null=True, blank=True)
    year = models.ForeignKey(Year, related_name='quotes', blank=True, null=True, on_delete=models.PROTECT)
    attributee_name = models.CharField(max_length=100, blank=True, null=True)
    attributee = models.ForeignKey(Entity, related_name='quotes', on_delete=models.PROTECT, null=True, blank=True)
    sources = models.ManyToManyField(Source, through=QuoteSourceReference, blank=True)

    searchable_fields = ['text', 'context', 'attributee__name', 'sources__title', 'year__common_era']

    class Meta:
        unique_together = [['date', 'attributee', 'bite']]

    def __str__(self):
        return f'{self.attributee or "<Unknown>"}: {self.text.text}'

    @property
    def image(self) -> Optional[Image]:
        if self.attributee and self.attributee.images.exists():
            if self.date:
                image = self.attributee.images.get_closest_to_datetime(self.date)
                return self.attributee.images.get_closest_to_datetime(self.date)
            return self.attributee.images.first()
        return None

    @property
    def slug(self) -> str:
        text = self.text.text
        if len(text) > 1000:
            return f'{text[:500]} ....... {text[-500:]}'
        return text

    @property
    def source_reference(self) -> Optional[QuoteSourceReference]:
        if not len(self.sources.all()):
            return None
        return self.source_references.order_by('position')[0]

    @property
    def source_file_url(self) -> Optional[str]:
        if self.source_reference:
            return self.source_reference.source_file_url
        return None

    def natural_key(self) -> Tuple:
        return self.date, self.attributee, self.bite

    def clean(self):
        super().clean()
        if not self.text and not self.context:
            raise ValidationError('The quote must have text or context.')
        if not self.bite:
            text = self.text.text
            self.bite = text
            if len(text) > 600:
                self.bite = f'{text[:300]} ....... {text[-300:]}'
        if self.date:
            self.year, _ = Year.objects.get_or_create(common_era=self.date.year)
        elif self.year:
            from datetime import date
            self.date = date(self.year.common_era, month=1, day=1)
            pass  # TODO

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
