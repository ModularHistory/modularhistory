from typing import Optional
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE
from django.utils.safestring import SafeText, mark_safe
# from gm2m import GM2MField as GenericManyToManyField
from entities.models import Entity
from history.fields import HTMLField, HistoricDateTimeField
from history.models import Model, TaggableModel, DatedModel, SearchableMixin, SourceMixin
from images.models import Image
from sources.models import Source, SourceReference, Citation
from .manager import Manager


class QuoteSourceReference(SourceReference):
    """A reference to a source."""
    quote = ForeignKey('Quote', related_name='citations', on_delete=CASCADE)
    source = ForeignKey(Source, related_name='references_from_quotes', on_delete=CASCADE)

    class Meta:
        verbose_name = 'citation'
        unique_together = ['quote', 'source']
        ordering = ['position', 'source', 'page_number']

    def __str__(self) -> SafeText:
        string = super().__str__()
        if self.source.attributees.exists():
            if self.quote.attributee != self.source.attributees.first():
                source_string = string
                string = f'{self.quote.attributee}'
                string += f', {self.quote.date_string}' if self.quote.date else ''
                string += f', quoted in {source_string}'
        return mark_safe(string)


class QuoteAttribution(Model):
    quote = ForeignKey('Quote', related_name='attributions', on_delete=CASCADE)
    attributee = ForeignKey(Entity, related_name='quote_attributions', on_delete=CASCADE)
    position = models.PositiveSmallIntegerField(default=0, blank=True)

    class Meta:
        unique_together = ['quote', 'attributee']
        ordering = ['position']

    def __str__(self):
        return str(self.attributee)

    def clean(self):
        super().clean()
        if self.position > 0 and len(QuoteAttribution.objects.exclude(pk=self.pk).filter(
                quote=self.quote, attributee=self.attributee, position=self.position
        )) > 1:
            raise ValidationError('Attribution position should be unique.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Quote(TaggableModel, DatedModel, SearchableMixin, SourceMixin):
    """A quote"""
    text = HTMLField()
    bite = HTMLField(null=True, blank=True)
    pretext = HTMLField(null=True, blank=True, help_text='Content to be displayed before the quote')
    context = HTMLField(null=True, blank=True, help_text='Content to be displayed after the quote')
    date = HistoricDateTimeField(null=True, blank=True)
    attributees = ManyToManyField(
        Entity, related_name='quotes2',
        through=QuoteAttribution,
        blank=True
    )
    # TODO: clean up (remove) attributee field; just use `attributees`
    attributee = ForeignKey(
        Entity, related_name='quotes',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    sources = ManyToManyField(
        Source, related_name='quotes',
        through=QuoteSourceReference,
        blank=True
    )
    # sources2 = GenericManyToManyField(Source, through=Citation, related_name='quotes', blank=True)

    class Meta:
        unique_together = ['date', 'attributee', 'bite']
        ordering = ['date']

    searchable_fields = [
        'text', 'context', 'attributee__name', 'date__year',
        'sources__db_string', 'related_topics__key', 'related_topics__aliases'
    ]
    objects: Manager = Manager()

    def __str__(self):
        return (f'{self.attributee_string or "<Unknown>"}'
                f'{(", " + self.date.string) if self.date else ""}: '
                f'{self.text.text}')

    @property
    def attributee_html(self) -> Optional[SafeText]:
        if not self.attributees.exists():
            return None
        attributions = self.attributions.all()
        n_attributions = len(attributions)
        first_attributee = attributions[0].attributee

        def _html(attributee) -> str:
            return (f'<a href="{reverse("entities:detail", args=[attributee.id])}" '
                    f'target="_blank">{attributee}</a>')

        html = _html(first_attributee)
        if n_attributions == 2:
            html += f' and {_html(attributions[1].attributee)}'
        elif n_attributions == 3:
            html = (f'{first_attributee}, {_html(attributions[1].attributee)}, '
                    f'and {_html(attributions[2].attributee)}')
        elif n_attributions > 3:
            html = f'{first_attributee} et al.'
        return mark_safe(html)

    @property
    def attributee_string(self) -> Optional[SafeText]:
        if not self.attributees.exists():
            return None
        attributions = self.attributions.all()
        n_attributions = len(attributions)
        first_attributee = attributions[0].attributee
        string = str(first_attributee)
        if n_attributions == 2:
            string += f' and {attributions[1].attributee}'
        elif n_attributions == 3:
            string += f', {attributions[1].attributee}, and {attributions[2].attributee}'
        elif n_attributions > 3:
            string += f' et al.'
        return mark_safe(string)

    @property
    def html(self) -> SafeText:
        html = f'<div class="quote-context">{self.pretext.html}</div>' if self.pretext else ''
        html += (
            f'<blockquote class="blockquote">'
            f'<a class="edit-object-button float-right" target="_blank" href="{self.admin_url}">'
            f'<i class="fa fa-edit"></i>'
            f'</a>'
            f'{self.text.html}'
            f'<footer class="blockquote-footer" style="position: relative;">'
            f'{self.citation_html or self.attributee_string}'
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
            if len(text) > 400:
                raise ValidationError('Add a quote bite.')
            self.bite = text
        # TODO: The logic below can be removed after the `attributee` field is removed
        if self.attributees.exists():
            if hasattr(self, 'attributee') and not getattr(self, 'attributee', None):
                self.attributee = self.attributees.first()
        elif getattr(self, 'attributee', None):
            QuoteAttribution.objects.create(quote=self, attributee=self.attributee)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class QuoteBite(TaggableModel):
    """A catchy piece of a larger quote."""
    quote = ForeignKey(Quote, on_delete=CASCADE, related_name='bites')
