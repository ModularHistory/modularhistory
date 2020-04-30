from typing import List, Optional, TYPE_CHECKING
from django.db.models import QuerySet, Q
from bs4 import BeautifulSoup
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE, ForeignKey, PositiveSmallIntegerField, ManyToManyField
from django.urls import reverse
from django.utils.safestring import SafeText, mark_safe
from gm2m import GM2MField as GenericManyToManyField

from entities.models import Entity
from history.fields import HTMLField, HistoricDateTimeField
from history.models import (
    Model, DatedModel, TaggableModel,
    RelatedQuotesMixin, SearchableMixin, SourcesMixin
)
from images.models import Image
from .manager import Manager

if TYPE_CHECKING:
    from entities.models import Classification, EntityClassification


class Quote(DatedModel, TaggableModel, RelatedQuotesMixin, SearchableMixin, SourcesMixin):
    """A quote"""
    text = HTMLField(verbose_name='Text')
    bite = HTMLField(verbose_name='Bite', null=True, blank=True)
    pretext = HTMLField(verbose_name='Pretext', null=True, blank=True,
                        help_text='Content to be displayed before the quote')
    context = HTMLField(verbose_name='Context', null=True, blank=True,
                        help_text='Content to be displayed after the quote')
    date = HistoricDateTimeField(null=True, blank=True)
    attributees = ManyToManyField(
        Entity, related_name='quotes',
        through='QuoteAttribution',
        blank=True
    )
    related = GenericManyToManyField(
        'occurrences.Occurrence', 'entities.Entity', 'quotes.Quote',
        through='QuoteRelation',
        related_name='related_quotes2',
        blank=True
    )

    class Meta:
        unique_together = ['date', 'bite']
        ordering = ['date']

    searchable_fields = [
        'text', 'context', 'attributees__name', 'date__year',
        'sources__db_string', 'tags__topic__key', 'tags__topic__aliases'
    ]
    objects: Manager = Manager()

    def __str__(self):
        return mark_safe(f'{self.attributee_string or "<Unknown>"}'
                         f'{(", " + self.date.string) if self.date else ""}: '
                         f'{self.bite.text}')

    # _attributee_html is defined as a method rather than a property
    # so that its `admin_order_field` attribute can be modified
    def _attributee_html(self) -> Optional[SafeText]:
        """See also the `attributee_string` property."""
        if not self.pk or not self.attributees.exists():
            return None
        attributees = self.ordered_attributees
        n_attributions = len(attributees)
        first_attributee = attributees[0]

        def _html(attributee) -> str:
            return (f'<a href="{reverse("entities:detail", args=[attributee.id])}" '
                    f'target="_blank">{attributee}</a>')

        html = _html(first_attributee)
        if n_attributions == 2:
            html += f' and {_html(attributees[1])}'
        elif n_attributions == 3:
            html += (f', {_html(attributees[1])}, '
                     f'and {_html(attributees[2])}')
        elif n_attributions > 3:
            html += f' et al.'
        return mark_safe(html)

    # TODO: Order by `attributee_string` instead of `attributee`
    _attributee_html.admin_order_field = 'attributee'
    attributee_html = property(_attributee_html)

    @property
    def attributee_string(self) -> Optional[SafeText]:
        """See the `attributee_html` property."""
        if not self.attributee_html:
            return None
        return BeautifulSoup(self.attributee_html, features='lxml').get_text()

    @property
    def html(self) -> SafeText:
        html = f'<div class="quote-context">{self.pretext.html}</div>' if self.pretext else ''
        html += (
            f'<blockquote class="blockquote">'
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
        if self.attributees.exists() and self.attributees.first().images.exists():
            attributee = self.attributees.first()
            if self.date:
                return attributee.images.get_closest_to_datetime(self.date)
            return attributee.images.first()
        elif self.related_occurrences.exists():
            return self.related_occurrences.first().image
        return None

    @property
    def ordered_attributees(self) -> Optional[List[Entity]]:
        if not self.pk or not self.attributees.exists():
            return None
        return [attribution.attributee for attribution in self.attributions.all()]

    @property
    def related_occurrences(self) -> QuerySet:
        # TODO: refactor
        from occurrences.models import Occurrence
        occurrence_ct = ContentType.objects.get_for_model(Occurrence)
        occurrence_ids = [
            o.id for o in self.relations.filter(Q(content_type_id=occurrence_ct.id))
        ]
        return Occurrence.objects.filter(id__in=occurrence_ids)

    @property
    def related_quotes(self) -> QuerySet:
        # TODO: refactor
        quote_ct = ContentType.objects.get_for_model(Quote)
        quote_ids = [
            q.id for q in self.relations.filter(Q(content_type_id=quote_ct.id))
        ]
        return Quote.objects.filter(id__in=quote_ids)

    def clean(self):
        super().clean()
        if (not self.text) or len(f'{self.text}') < 15:  # e.g., <p>&nbsp;</p>
            raise ValidationError('The quote must have text.')
        if not self.bite:
            text = self.text.text
            if len(text) > 400:
                raise ValidationError('Add a quote bite.')
            self.bite = text

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


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


class QuoteBite(TaggableModel):
    """A catchy piece of a larger quote."""
    quote = ForeignKey(Quote, on_delete=CASCADE, related_name='bites')


class QuoteRelation(Model):
    """A relation to a quote (by any other model)."""
    quote = ForeignKey(Quote, related_name='relations', on_delete=CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    position = PositiveSmallIntegerField(
        null=True, blank=True,  # TODO: add cleaning logic
        help_text='Determines the order of quotes.'
    )

    def __str__(self):
        return BeautifulSoup(self.quote.bite.html, features='lxml').get_text()

    class Meta:
        unique_together = ['quote', 'content_type', 'object_id', 'position']
        ordering = ['position', 'quote']

    @property
    def quote_pk(self) -> str:
        return self.quote.pk


def quote_sorter_key(quote: Quote):
    x = 0
    if quote.date:
        date = quote.date
        x += 1000000000000*date.year + 1000000000*date.month + 1000000*date.day
    if quote.citation:
        citation = quote.citation
        number = ord(str(citation)[0].lower()) - 96
        x += number*1000
        if citation.page_number:
            x += citation.page_number
    return x
