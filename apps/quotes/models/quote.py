"""Model classes for the quotes app."""

import logging
import re
from typing import TYPE_CHECKING, List, Optional

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.text import slugify
from gm2m import GM2MField as GenericManyToManyField

from apps.entities.models.model_with_related_entities import ModelWithRelatedEntities
from apps.images.models.model_with_images import ModelWithImages
from apps.quotes.manager import QuoteManager
from apps.quotes.models.model_with_related_quotes import ModelWithRelatedQuotes
from apps.quotes.models.quote_image import QuoteImage
from apps.quotes.serializers import QuoteSerializer
from apps.search.models import SearchableDatedModel
from apps.sources.models.model_with_sources import ModelWithSources
from modularhistory.constants.strings import EMPTY_STRING
from modularhistory.fields import HistoricDateTimeField, HTMLField
from modularhistory.fields.html_field import (
    OBJECT_PLACEHOLDER_REGEX,
    TYPE_GROUP,
    PlaceholderGroups,
)
from modularhistory.models import retrieve_or_compute
from modularhistory.utils.html import soupify

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.entities.models import Entity

BITE_MAX_LENGTH: int = 400

quote_placeholder_regex = OBJECT_PLACEHOLDER_REGEX.replace(
    TYPE_GROUP, rf'(?P<{PlaceholderGroups.MODEL_NAME}>quote)'
)


class Quote(
    SearchableDatedModel,
    ModelWithSources,
    ModelWithRelatedQuotes,
    ModelWithRelatedEntities,
    ModelWithImages,
):
    """A quote."""

    text = HTMLField(verbose_name='text', paragraphed=True)
    bite = HTMLField(verbose_name='bite', null=True, blank=True)
    pretext = HTMLField(
        verbose_name='pretext',
        null=True,
        blank=True,
        paragraphed=False,
        help_text='Content to be displayed before the quote',
    )
    context = HTMLField(
        verbose_name='context',
        null=True,
        blank=True,
        paragraphed=True,
        help_text='Content to be displayed after the quote',
    )
    date = HistoricDateTimeField(null=True)
    attributees = models.ManyToManyField(
        to='entities.Entity',
        through='quotes.QuoteAttribution',
        related_name='quotes',
        blank=True,
    )
    related = GenericManyToManyField(
        'occurrences.Occurrence',
        'entities.Entity',
        'quotes.Quote',
        through='quotes.QuoteRelation',
        related_name='related_quotes',
        blank=True,
    )
    images = models.ManyToManyField(
        'images.Image', through='quotes.QuoteImage', related_name='quotes', blank=True
    )

    class Meta:
        """
        Meta options for Quote.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        unique_together = ['date', 'bite']
        ordering = ['date']

    objects: QuoteManager = QuoteManager()  # type: ignore
    placeholder_regex = quote_placeholder_regex
    searchable_fields = [
        'text',
        'context',
        'attributees__name',
        'date__year',
        'sources__full_string',
        'tags__topic__key',
        'tags__topic__aliases',
    ]
    serializer = QuoteSerializer

    def __str__(self) -> str:
        """Return the quote's string representation, for debugging and internal use."""
        # Avoid recursion errors by checking for pk
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
                attributee: 'Entity' = self.attributees.first()
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
    def attributee_html(self) -> SafeString:
        """Return the HTML representing the quote's attributees."""
        logging.debug('Computing attributee HTML...')
        attributees = self.ordered_attributees
        attributee_html = ''
        if attributees:
            n_attributions = len(attributees)
            primary_attributee = attributees[0]
            primary_attributee_html = primary_attributee.get_detail_link(
                primary_attributee.name
            )
            if n_attributions == 1:
                attributee_html = f'{primary_attributee_html}'
            else:
                secondary_attributee_html = (
                    f'{attributees[1].get_detail_link(attributees[1].name)}'
                )
                if n_attributions == 2:
                    attributee_html = (
                        f'{primary_attributee_html} and {secondary_attributee_html}'
                    )
                elif n_attributions == 3:
                    attributee_html = (
                        f'{primary_attributee_html}, {secondary_attributee_html}, and '
                        f'{attributees[2].get_detail_link(attributees[2].name)}'
                    )
                else:
                    attributee_html = f'{primary_attributee_html} et al.'
        return format_html(attributee_html)

    # TODO: Order by `attributee_string` instead of `attributee`
    attributee_html.admin_order_field = 'attributee'
    attributee_html: SafeString = property(attributee_html)  # type: ignore

    def get_slug(self) -> str:
        """Generate a slug for the quote."""
        return slugify(self.pk)

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
    def attributee_string(self) -> Optional[str]:
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
            f'<p class="quote-context">{self.pretext.html}</p>'
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
    def ordered_attributees(self) -> Optional[List['Entity']]:
        """
        Return an ordered list of the quote's attributees.

        WARNING: This queries the database.
        """
        try:
            attributions = self.attributions.select_related('attributee').iterator()
            return [attribution.attributee for attribution in attributions]
        except (AttributeError, ObjectDoesNotExist) as error:
            logging.error(f'>>> {type(error)}: {error}')
            return None

    @property
    def related_occurrences(self) -> 'QuerySet':
        """Return a queryset of the quote's related occurrences."""
        # TODO: refactor
        from apps.occurrences.models import Occurrence
        from modularhistory.constants.content_type_ids import OCCURRENCE_CT_ID

        occurrence_ids = self.relations.filter(
            models.Q(content_type_id=OCCURRENCE_CT_ID)
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
            preretrieved_html = match.group(PlaceholderGroups.HTML)
            if preretrieved_html:
                return preretrieved_html.strip()
        quote = cls.objects.get(pk=match.group(PlaceholderGroups.PK))
        if isinstance(quote, dict):
            body = quote['text']
            footer = quote.get('citation_html') or quote.get('attributee_string')
        else:
            body = quote.text.html
            footer = quote.citation_html or quote.attributee_string
        return (
            f'<blockquote class="blockquote">'
            f'{body}'
            f'<footer class="blockquote-footer" style="position: relative;">'
            f'{footer}'
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
