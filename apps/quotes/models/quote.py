"""Model classes for the quotes app."""

import logging
from typing import TYPE_CHECKING, Match

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import Serializer

from apps.collections.models import AbstractCollectionInclusion
from apps.dates.fields import HistoricDateTimeField
from apps.dates.models import DatedModel
from apps.entities.models.model_with_related_entities import (
    AbstractEntityRelation,
    ModelWithRelatedEntities,
    RelatedEntitiesField,
)
from apps.images.models.model_with_images import (
    AbstractImageRelation,
    ImagesField,
    ModelWithImages,
)
from apps.quotes.models.model_with_related_quotes import (
    AbstractQuoteRelation,
    ModelWithRelatedQuotes,
    RelatedQuotesField,
)
from apps.sources.models.citation import AbstractCitation
from apps.sources.models.model_with_sources import ModelWithSources, SourcesField
from apps.topics.models.taggable import AbstractTopicRelation, TaggableModel, TagsField
from core.constants.strings import EMPTY_STRING
from core.fields.html_field import (
    OBJECT_PLACEHOLDER_REGEX,
    TYPE_GROUP,
    HTMLField,
    PlaceholderGroups,
)
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.module import Module
from core.utils.html import soupify

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.entities.models.entity import Entity

TEXT_MIN_LENGTH: int = 15
BITE_MAX_LENGTH: int = 400

quote_placeholder_regex = OBJECT_PLACEHOLDER_REGEX.replace(
    TYPE_GROUP, rf'(?P<{PlaceholderGroups.MODEL_NAME}>quote)'  # noqa: WPS360
)


def get_quote_fk(related_name: str) -> ManyToManyForeignKey:
    """Return a foreign key field referencing a quote."""
    return ManyToManyForeignKey(
        to='quotes.Quote',
        related_name=related_name,
        verbose_name='quote',
    )


class CollectionInclusion(AbstractCollectionInclusion):
    """An inclusion of a proposition in a collection."""

    content_object = get_quote_fk(related_name='collection_inclusions')


class Citation(AbstractCitation):
    """A relationship between a quote and a source."""

    content_object = get_quote_fk(related_name='citations')

    @classmethod
    def get_serializer(self) -> Serializer:
        """Return the serializer for the entity."""
        from apps.quotes.api.serializers import CitationSerializer

        return CitationSerializer


class ImageRelation(AbstractImageRelation):
    """A relationship between a quote and an image."""

    content_object = get_quote_fk(related_name='image_relations')


class QuoteRelation(AbstractQuoteRelation):
    """A relationship between a quote and another quote."""

    content_object = get_quote_fk(related_name='quote_relations')


class EntityRelation(AbstractEntityRelation):
    """A relationship between a quote and an entity."""

    content_object = get_quote_fk(related_name='entity_relations')


class TopicRelation(AbstractTopicRelation):
    """A relationship between a quote and a topic."""

    content_object = get_quote_fk(related_name='topic_relations')


class Quote(
    Module,
    TaggableModel,
    DatedModel,
    ModelWithSources,
    ModelWithRelatedQuotes,
    ModelWithRelatedEntities,
    ModelWithImages,
):
    """A quote."""

    text = HTMLField(verbose_name='text', paragraphed=True, processed=False)
    bite = HTMLField(verbose_name='bite', blank=True, processed=False)
    pretext = HTMLField(
        verbose_name='pretext',
        blank=True,
        paragraphed=False,
        help_text='Content to be displayed before the quote',
    )
    context = HTMLField(
        verbose_name='context',
        blank=True,
        paragraphed=True,
        help_text='Content to be displayed after the quote',
    )
    date = HistoricDateTimeField(null=True)
    attributee_html = models.TextField(
        verbose_name=_('attributee HTML'),
        blank=True,
        editable=False,
    )
    attributees = models.ManyToManyField(
        to='entities.Entity',
        through='quotes.QuoteAttribution',
        related_name='quotes',
        blank=True,
        verbose_name=_('attributees'),
    )
    images = ImagesField(through=ImageRelation)
    sources = SourcesField(through=Citation, related_name='quotes')
    related_quotes = RelatedQuotesField(
        through=QuoteRelation,
        to='self',
        symmetrical=False,
        through_fields=('content_object', 'quote'),
    )
    related_entities = RelatedEntitiesField(through=EntityRelation)
    tags = TagsField(through=TopicRelation)

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        ordering = ['date']

    placeholder_regex = quote_placeholder_regex
    searchable_fields = [
        'text',
        'context',
        'attributees__name',
        'date__year',
        'sources__citation_string',
        'tags__name',
        'tags__aliases',
    ]
    slug_base_fields = ('title',)

    @classmethod
    def get_serializer(self) -> type[Serializer]:
        """Return the serializer for the entity."""
        from apps.quotes.api.serializers import QuoteSerializer

        return QuoteSerializer

    def __str__(self) -> str:
        """Return the quote's string representation, for debugging and internal use."""
        # Avoid recursion errors by checking for pk
        attributee_string = self.attributee_string or '<Unknown>'
        date_string = self.date.string if self.date else EMPTY_STRING
        if date_string:
            string = f'{attributee_string}, {date_string}: {self.bite}'
        else:
            string = f'{attributee_string}: {self.bite}'
        return string

    def clean(self):
        super().clean()
        no_text = not self.text
        if no_text or len(f'{self.text}') < TEXT_MIN_LENGTH:  # e.g., <p>&nbsp;</p>
            raise ValidationError(
                f'The quote must have text or too short (min_length={TEXT_MIN_LENGTH}).'
            )
        if not self.bite:
            text = self.text
            if len(text) > BITE_MAX_LENGTH:
                raise ValidationError('Add a quote bite.')
            self.bite = text  # type: ignore  # TODO: remove type ignore
        self.update_calculated_fields()

    def post_save(self, *args, **kwargs):
        super().post_save()
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
                ImageRelation.objects.create(content_object=self, image=image)

    def update_calculated_fields(self):
        """Update the quote's calculated fields."""
        self.attributee_html = self.get_attributee_html()
        self.title = self.title or ', '.join(
            [item for item in (self.attributee_string, self.date_string) if item]
        )

    def get_attributee_html(self) -> SafeString:
        """Return the HTML representing the quote's attributees."""
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

    @property
    def escaped_attributee_html(self) -> SafeString:
        """Return the escaped attributee HTML to be displayed in the Django admin."""
        return format_html(self.attributee_html)

    @property
    def has_multiple_attributees(self) -> bool:
        """
        Return True if the quote has multiple attributees, else False.

        This method minimizes db query complexity.
        """
        if self.attributee_html:
            attributee_html: str = self.attributee_html
            signals = (' and ', ', ', ' et al.')
            for signal in signals:
                if signal in attributee_html:
                    return True
        return False

    @property
    def attributee_string(self) -> str:
        """See the `attributee_html` property."""
        if self.attributee_html:
            return soupify(self.attributee_html).get_text()  # type: ignore
        return ''

    @property
    def html(self) -> SafeString:
        """Return the quote's HTML representation."""
        blockquote = (
            f'<blockquote class="blockquote">'
            f'{self.text}'
            f'<footer class="blockquote-footer" style="position: relative;">'
            f'{self.citation_html or self.attributee_string}'
            f'</footer>'
            f'</blockquote>'
        )
        components = [
            f'<p class="quote-context">{self.pretext}</p>' if self.pretext else EMPTY_STRING,
            blockquote,
            f'<div class="quote-context">{self.context}</div>'
            if self.context
            else EMPTY_STRING,
        ]
        html = '\n'.join([component for component in components if component])
        return format_html(html)

    @property
    def ordered_attributees(self) -> list['Entity']:
        """
        Return an ordered list of the quote's attributees.

        WARNING: This queries the database.
        """
        try:
            attributions = self.attributions.select_related('attributee').iterator()
            return [attribution.attributee for attribution in attributions]
        except (AttributeError, ObjectDoesNotExist) as error:
            logging.error(f'{type(error)}: {error}')
            return []

    @property
    def related_occurrences(self) -> 'QuerySet':
        """Return a queryset of the quote's related occurrences."""
        # TODO: refactor
        from apps.propositions.models.occurrence import Occurrence

        return Occurrence.objects.filter(related_quotes__pk=self.pk)

    @classmethod
    def get_object_html(cls, match: Match, use_preretrieved_html: bool = False) -> str:
        """Return the quote's HTML based on a placeholder in the admin."""
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = str(match.group(PlaceholderGroups.HTML))
            if preretrieved_html:
                return str(preretrieved_html).strip()
        quote = cls.objects.get(pk=match.group(PlaceholderGroups.PK))
        if isinstance(quote, dict):
            body = quote['text']
            footer = quote.get('citation_html') or quote.get('attributee_string')
        else:
            body = quote.text
            footer = quote.citation_html or quote.attributee_string
        return (
            f'<blockquote class="blockquote">'
            f'{body}'
            f'<footer class="blockquote-footer" style="position: relative;">'
            f'{footer}'
            f'</footer>'
            f'</blockquote>'
        )


def quote_sorter_key(quote: Quote) -> int:
    """Return an integer used to position a quote relative to other quotes."""
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
