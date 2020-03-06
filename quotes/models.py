from typing import Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE
from django.utils.safestring import SafeText, mark_safe

from entities.models import Entity
from history.fields.historic_datetime_field import HistoricDateTimeField
from history.fields.html_field import HTMLField
from history.models import Model, TaggableModel, DatedModel, SearchableMixin
from images.models import Image
from sources.models import Source, SourceReference
from .manager import Manager


class QuoteSourceReference(SourceReference):
    """A reference to a source."""
    quote = ForeignKey('Quote', related_name='source_references', on_delete=models.CASCADE)
    source = ForeignKey(Source, related_name='references_from_quotes', on_delete=models.CASCADE)

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


class Quote(TaggableModel, DatedModel, SearchableMixin):
    """A quote"""
    objects: Manager = Manager()

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

    searchable_fields = ['text', 'context', 'attributee__name', 'date__year',
                         'sources__db_string', 'related_topics__key', 'related_topics__aliases']

    def __str__(self):
        return (f'{self.attributee or "<Unknown>"}'
                f'{(", " + self.date.string) if self.date else ""}: '
                f'{self.text.text}')

    @property
    def html(self):
        source_reference_html = str(self.attributee)
        if self.source_reference:
            source_reference_html = f'{self.source_reference.html} '
        html = f'<div class="quote-context">{self.pretext.html}</div>' if self.pretext else ''
        html += (
            f'<blockquote class="blockquote">'
            f'{self.text.html}'
            f'<footer class="blockquote-footer" style="position: relative;">'
            f'{source_reference_html}'
            f'<a class="edit-object-button" target="_blank" href="{self.get_admin_url()}">'
            f'<i class="fa fa-edit"></i>'
            f'</a>'
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
