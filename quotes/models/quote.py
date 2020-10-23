"""Model classes for the quotes app."""

import re
from typing import List, Optional

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import ManyToManyField, Q, QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from gm2m import GM2MField as GenericManyToManyField

from entities.models import Entity
from images.models import Image
from modularhistory.constants import EMPTY_STRING, OCCURRENCE_CT_ID
from modularhistory.fields import HTMLField, HistoricDateTimeField
from modularhistory.models import (
    DatedModel,
    ModelWithImages,
    ModelWithRelatedEntities,
    ModelWithRelatedQuotes,
    ModelWithSources,
    retrieve_or_compute,
)
from modularhistory.utils.html import soupify
from quotes.manager import QuoteManager
from quotes.models.quote_image import QuoteImage

BITE_MAX_LENGTH: int = 400


class Quote(
    DatedModel,
    ModelWithSources,
    ModelWithRelatedQuotes,
    ModelWithRelatedEntities,
    ModelWithImages,
):
    """A quote."""

    text = HTMLField(verbose_name='Text')
    bite = HTMLField(verbose_name='Bite', null=True, blank=True)
    pretext = HTMLField(
        verbose_name='Pretext',
        null=True,
        blank=True,
        help_text='Content to be displayed before the quote',
    )
    context = HTMLField(
        verbose_name='Context',
        null=True,
        blank=True,
        help_text='Content to be displayed after the quote',
    )
    date = HistoricDateTimeField(null=True)
    attributees = ManyToManyField(
        Entity, through='quotes.QuoteAttribution', related_name='quotes', blank=True
    )
    related = GenericManyToManyField(
        'occurrences.Occurrence',
        'entities.Entity',
        'quotes.Quote',
        through='quotes.QuoteRelation',
        related_name='related_quotes',
        blank=True,
    )
    images = ManyToManyField(
        Image, through='quotes.QuoteImage', related_name='quotes', blank=True
    )

    class Meta:
        unique_together = ['date', 'bite']
        ordering = ['date']

    class FieldNames(ModelWithSources.FieldNames):
        text = 'text'
        attributees = 'attributees'

    searchable_fields = [
        FieldNames.text,
        'context',
        f'{FieldNames.attributees}__name',
        'date__year',
        'sources__full_string',
        'tags__topic__key',
        'tags__topic__aliases',
    ]
    objects: QuoteManager = QuoteManager()  # type: ignore

    def __str__(self) -> str:
        """Return the quote's string representation, for debugging and internal use."""
        attributee_string = self.attributee_string or '<Unknown>'
        date_string = self.date.string if self.date else EMPTY_STRING
        if date_string:
            string = f'{attributee_string}, {date_string}: {self.bite.text}'
        else:
            string = f'{attributee_string}: {self.bite.text}'
        return string

    def save(self, *args, **kwargs):
        """Save the quote to the database."""
        self.clean()
        super().save(*args, **kwargs)
        if not self.images.exists():
            image = None
            try:
                attributee = self.attributees.first()
                if self.date:
                    image = attributee.images.get_closest_to_datetime(self.date)
                else:
                    image = attributee.images.first()
            except (ObjectDoesNotExist, AttributeError):
                pass
            if image is None and self.related_occurrences.exists():
                image = self.related_occurrences.first().primary_image
            if image:
                QuoteImage.objects.create(quote=self, image=image)

    @retrieve_or_compute(attribute_name='attributee_html', caster=format_html)
    def attributee_html(self) -> Optional[SafeString]:
        """Return the HTML representing the quote's attributees."""
        attributees = self.ordered_attributees
        if attributees:
            n_attributions = len(attributees)
            first_attributee = attributees[0]

            def _html(attributee) -> str:
                return (
                    f'<a href="{reverse("entities:detail", args=[attributee.id])}" '
                    f'target="_blank">{attributee}</a>'
                )

            html = _html(first_attributee)
            if n_attributions == 2:
                html = f'{html} and {_html(attributees[1])}'
            elif n_attributions == 3:
                html = f'{html}, {_html(attributees[1])}, and {_html(attributees[2])}'
            elif n_attributions > 3:
                html = f'{html} et al.'
            attributee_html = html
        else:
            attributee_html = EMPTY_STRING
        return format_html(attributee_html) if attributee_html else None

    # TODO: Order by `attributee_string` instead of `attributee`
    attributee_html.admin_order_field = 'attributee'
    attributee_html: SafeString = property(attributee_html)  # type: ignore

    @property
    def has_multiple_attributees(self) -> bool:
        """
        Return True if the quote has multiple attributees, else False.

        This method minimizes db query complexity.
        """
        attributee_html: str = self.attributee_html  # type: ignore
        signals = (' and ', ', ', ' et al.')
        for signal in signals:
            if signal in attributee_html:
                return True
        return False

    @property
    def attributee_string(self) -> Optional[SafeString]:
        """See the `attributee_html` property."""
        if self.attributee_html:
            return soupify(self.attributee_html).get_text()  # type: ignore
        return None

    @property
    def html(self) -> SafeString:
        """Return the quote's HTML representation."""
        blockquote = (
            f'<blockquote class="blockquote">'
            f'{self.text.html}'
            f'<footer class="blockquote-footer" style="position: relative;">'
            f'{self.citation_html or self.attributee_string}'
            f'</footer>'
            f'</blockquote>'
        )
        components = [
            f'<div class="quote-context">{self.pretext.html}</div>'
            if self.pretext
            else EMPTY_STRING,
            blockquote,
            f'<div class="quote-context">{self.context.html}</div>'
            if self.context
            else EMPTY_STRING,
        ]
        html = '\n'.join([component for component in components if component])
        return format_html(html)

    @property
    def ordered_attributees(self) -> Optional[List[Entity]]:
        """
        Return an ordered list of the quote's attributees.

        WARNING: This queries the database.
        """
        try:
            attributions = self.attributions.select_related('attributee')
            return [attribution.attributee for attribution in attributions]
        except (AttributeError, ObjectDoesNotExist) as error:
            print(f'>>> {type(error)}: {error}')
            return None

    @property
    def related_occurrences(self) -> QuerySet:
        """Return a queryset of the quote's related occurrences."""
        # TODO: refactor
        from occurrences.models import Occurrence

        occurrence_ids = self.relations.filter(
            Q(content_type_id=OCCURRENCE_CT_ID)
        ).values_list('id', flat=True)
        return Occurrence.objects.filter(id__in=occurrence_ids)

    def clean(self):
        """Prepare the quote to be saved to the database."""
        super().clean()
        no_text = not self.text
        min_text_length = 15
        if no_text or len(f'{self.text}') < min_text_length:  # e.g., <p>&nbsp;</p>
            raise ValidationError('The quote must have text.')
        if not self.bite:
            text = self.text.text
            if len(text) > BITE_MAX_LENGTH:
                raise ValidationError('Add a quote bite.')
            self.bite = text  # type: ignore  # TODO: remove type ignore

    @classmethod
    def get_object_html(
        cls, match: re.Match, use_preretrieved_html: bool = False
    ) -> str:
        """Return the obj's HTML based on a placeholder in the admin."""
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(4)
            if preretrieved_html:
                return preretrieved_html.strip()
        quote = cls.get_object_from_placeholder(match)
        return (
            f'<blockquote class="blockquote">'
            f'{quote.text.html}'
            f'<footer class="blockquote-footer" style="position: relative;">'
            f'{quote.citation_html or quote.attributee_string}'
            f'</footer>'
            f'</blockquote>'
        )


def quote_sorter_key(quote: Quote):
    """TODO: add docstring."""
    level_multiplier = 1000
    day_multiplier = 1000000
    month_multiplier = day_multiplier * level_multiplier
    year_multiplier = month_multiplier * level_multiplier
    sorter_int = 0
    if quote.date:
        date = quote.date
        sorter_int += (
            (year_multiplier * date.year)
            + (month_multiplier * date.month)
            + (day_multiplier * date.day)
        )
    if quote.citation:
        citation = quote.citation
        magic_number = 96  # TODO: remember what this is
        number = ord(str(citation)[0].lower()) - magic_number
        sorter_int += number * 1000
        if citation.primary_page_number:
            sorter_int += citation.primary_page_number
    return sorter_int
