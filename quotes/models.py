from typing import Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, ManyToManyField

from entities.models import Entity
from history.fields import HTMLField, HistoricDateTimeField, HistoricDateTime
from history.models import Model, TaggableModel
from images.models import Image
from occurrences.models import Year
from sources.models import Source, SourceReference
from django.utils.safestring import SafeText, mark_safe


class QuoteSourceReference(SourceReference):
    """A reference to a source."""
    quote = ForeignKey('Quote', related_name='source_references', on_delete=models.CASCADE)
    source = ForeignKey(Source, related_name='references_from_quotes', on_delete=models.CASCADE)

    def __str__(self) -> SafeText:
        string = super().__str__()
        if self.source.attributees.exists():
            if self.quote.attributee != self.source.attributees.first():
                string = f'{self.quote.attributee}, quoted in {string}'
        return mark_safe(string)


class Quote(TaggableModel):
    """A quote"""
    text = HTMLField()
    bite = HTMLField(null=True, blank=True)
    context = HTMLField(null=True, blank=True)
    date = HistoricDateTimeField(null=True, blank=True)
    year = ForeignKey(Year, related_name='quotes', blank=True, null=True, on_delete=models.PROTECT)
    attributee_name = models.CharField(max_length=100, blank=True, null=True)
    attributee = ForeignKey(Entity, related_name='quotes', on_delete=models.PROTECT, null=True, blank=True)
    sources = ManyToManyField(Source, through=QuoteSourceReference, related_name='quotes', blank=True)

    class Meta:
        unique_together = [['date', 'attributee', 'bite']]

    searchable_fields = ['text', 'context', 'attributee__name', 'date__year',
                         'sources__db_string', 'related_topics__key', 'related_topics__aliases']

    def __str__(self):
        return (f'{self.attributee or self.attributee_name or "<Unknown>"}'
                f'{(", " + self.date.string) if self.date else ""}: '
                f'{self.text.text}')

    @property
    def image(self) -> Optional[Image]:
        if self.attributee and self.attributee.images.exists():
            if self.date:
                return self.attributee.images.get_closest_to_datetime(self.date)
            return self.attributee.images.first()
        elif self.related_occurrences.exists():
            return self.related_occurrences.first().image
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
            if len(text) > 400:
                self.bite = f'{text[:200]} ....... {text[-200:]}'
        if self.date:
            self.year, _ = Year.objects.get_or_create(common_era=self.date.year)
        elif self.year:
            self.date = HistoricDateTime(self.year.common_era, month=1, day=1, hour=1, minute=1, second=1)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
