from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE
from django.utils.safestring import SafeText, mark_safe

from entities.models import Entity
from history.fields import HTMLField, HistoricDateTimeField
from history.models import Model, TaggableModel, DatedModel, SearchableMixin, SourceMixin
from images.models import Image
from sources.models import Source, SourceReference
from .manager import Manager


class QuoteSourceReference(SourceReference):
    """A reference to a source."""
    quote = ForeignKey('Quote', related_name='source_references', on_delete=CASCADE)
    source = ForeignKey(Source, related_name='references_from_quotes', on_delete=CASCADE)

    class Meta:
        unique_together = ['quote', 'source']
        ordering = ['source', 'page_number']

    def __str__(self) -> SafeText:
        string = super().__str__()
        if self.source.attributees.exists():
            if self.quote.attributee != self.source.attributees.first():
                source_string = string
                string = f'{self.quote.attributee}'
                string += f', {self.quote.date_string}' if self.quote.date else ''
                string += f', quoted in {source_string}'
        return mark_safe(string)


class Quote(TaggableModel, DatedModel, SearchableMixin, SourceMixin):
    """A quote"""
    text = HTMLField()
    bite = HTMLField(null=True, blank=True)
    pretext = HTMLField(null=True, blank=True, help_text='Content to be displayed before the quote')
    context = HTMLField(null=True, blank=True, help_text='Content to be displayed after the quote')
    date = HistoricDateTimeField(null=True, blank=True)
    attributee = ForeignKey(
        Entity, related_name='quotes',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    sources = ManyToManyField(Source, through=QuoteSourceReference, related_name='quotes', blank=True)

    class Meta:
        unique_together = ['date', 'attributee', 'bite']
        ordering = ['date']

    searchable_fields = [
        'text', 'context', 'attributee__name', 'date__year',
        'sources__db_string', 'related_topics__key', 'related_topics__aliases'
    ]
    objects: Manager = Manager()

    def __str__(self):
        return (f'{self.attributee or "<Unknown>"}'
                f'{(", " + self.date.string) if self.date else ""}: '
                f'{self.text.text}')

    @property
    def html(self) -> SafeText:
        html = f'<div class="quote-context">{self.pretext.html}</div>' if self.pretext else ''
        html += (
            f'<blockquote class="blockquote">'
            f'<a class="edit-object-button float-right" target="_blank" href="{self.get_admin_url()}">'
            f'<i class="fa fa-edit"></i>'
            f'</a>'
            f'{self.text.html}'
            f'<footer class="blockquote-footer" style="position: relative;">'
            f'{self.source_reference_html or self.attributee}'
            f'</footer>'
            f'</blockquote>'
        )
        html += f'<div class="quote-context">{self.context.html}</div>' if self.context else ''
        return mark_safe(html)

    @property
    def image(self) -> Optional[Image]:
        if self.attributee and self.attributee.images.exists():
            if self.date:
                return self.attributee.images.get_closest_to_datetime(self.date)
            return self.attributee.images.first()
        elif self.related_occurrences.exists():
            return self.related_occurrences.first().image
        return None

    def clean(self):
        super().clean()
        if (not self.text) or len(f'{self.text}') < 15:  # e.g., <p>&nbsp;</p>
            raise ValidationError('The quote must have text.')
        if not self.bite:
            text = self.text.text
            self.bite = text
            if len(text) > 400:
                self.bite = f'{text[:200]} ....... {text[-200:]}'

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class QuoteBite(TaggableModel):
    """A catchy piece of a larger quote."""
    quote = ForeignKey(Quote, on_delete=CASCADE, related_name='bites')
