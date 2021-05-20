"""Model classes for propositions."""

import logging
import re
from typing import Match, Optional

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from apps.dates.models import DatedModel
from apps.entities.models.model_with_related_entities import ModelWithRelatedEntities
from apps.images.models.model_with_images import ModelWithImages
from apps.places.models.model_with_locations import ModelWithLocations
from apps.propositions.api.serializers import PropositionSerializer
from apps.quotes.models.model_with_related_quotes import (
    AbstractQuoteRelation,
    ModelWithRelatedQuotes,
    RelatedQuotesField,
)
from apps.search.models import SearchableModel
from apps.sources.models.citation import AbstractCitation
from apps.sources.models.model_with_sources import ModelWithSources, SourcesField
from core.fields import HTMLField
from core.fields.html_field import (
    OBJECT_PLACEHOLDER_REGEX,
    TYPE_GROUP,
    PlaceholderGroups,
)
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models import TypedModel
from core.utils.html import escape_quotes
from core.utils.string import dedupe_newlines, truncate

proposition_placeholder_regex = OBJECT_PLACEHOLDER_REGEX.replace(
    TYPE_GROUP, rf'(?P<{PlaceholderGroups.MODEL_NAME}>proposition)'
)
logging.debug(f'Proposition placeholder pattern: {proposition_placeholder_regex}')


DEGREES_OF_CERTAINTY = (
    (0, 'No credible evidence'),
    (1, 'Some credible evidence'),
    (2, 'A preponderance of evidence'),
    (3, 'Beyond reasonable doubt'),
    (4, 'Beyond any shadow of a doubt'),
)


def get_proposition_fk(related_name: str):
    return ManyToManyForeignKey(
        to='propositions.TypedProposition',
        related_name=related_name,
        verbose_name='proposition',
    )


class Citation(AbstractCitation):
    """A relation of a source with a proposition."""

    new_content_object = get_proposition_fk('citations')


class QuoteRelation(AbstractQuoteRelation):
    """A relation of a quote with a proposition."""

    new_content_object = get_proposition_fk('quote_relations')


class TypedProposition(
    TypedModel,
    SearchableModel,
    DatedModel,  # submodels like `Occurrence` require date
    ModelWithSources,
    ModelWithRelatedEntities,
    ModelWithRelatedQuotes,
    ModelWithLocations,
    ModelWithImages,
):
    """
    A proposition.

    Models of which instances are proposed, i.e., presented as information that
    can be analyzed and judged to be true or false with some degree of certainty,
    should inherit from this model.
    """

    summary = HTMLField(
        verbose_name=_('summary'), unique=True, paragraphed=False, processed=False
    )
    elaboration = HTMLField(verbose_name=_('elaboration'), null=True, paragraphed=True)
    certainty = models.PositiveSmallIntegerField(
        verbose_name=_('certainty'), null=True, choices=DEGREES_OF_CERTAINTY
    )
    premises = models.ManyToManyField(
        to='self',
        through='propositions.Support',
        related_name='conclusions',
        symmetrical=False,
        verbose_name=_('premises'),
    )
    related_quotes = RelatedQuotesField(
        through=QuoteRelation,
        related_name='new_propositions',
    )
    sources = SourcesField(
        through=Citation,
        related_name='new_propositions',
    )

    searchable_fields = [
        'title',
        'summary',
        'elaboration',
        'related_entities__name',
        'related_entities__aliases',
        'tags__key',
        'tags__aliases',
    ]
    serializer = PropositionSerializer
    slug_base_field = 'summary'

    def __str__(self) -> str:
        """Return the proposition's string representation."""
        return self.summary.text

    @property
    def summary_link(self) -> str:
        """Return an HTML link to the proposition, containing the summary text."""
        add_elaboration_tooltip = False
        elaboration = self.elaboration.html if self.elaboration else ''
        elaboration = elaboration.replace('\n', '')
        if add_elaboration_tooltip:
            summary_link = (
                f'<a href="{reverse("propositions:detail", args=[self.pk])}"'
                ' class="proposition-link" target="_blank" '
                f'title="{escape_quotes(elaboration)}" '
                f'data-toggle="tooltip" data-html="true">{self.summary.html}'
                '</a>'
            )
        else:
            summary_link = (
                f'<a href="{reverse("propositions:detail", args=[self.pk])}"'
                ' class="proposition-link" target="_blank">'
                f'{self.summary.html}'
                '</a>'
            )
        return summary_link

    @classmethod
    def get_object_html(cls, match: Match, use_preretrieved_html: bool = False) -> str:
        """Return the proposition's HTML based on a placeholder in the admin."""
        if not match:
            logging.error('proposition.get_object_html was called without a match')
            raise ValueError
        if use_preretrieved_html:
            # Return the pre-retrieved HTML (already included in placeholder)
            preretrieved_html = match.group(PlaceholderGroups.HTML)
            if preretrieved_html:
                return str(preretrieved_html).strip()
        pk = int(match.group(PlaceholderGroups.PK))
        proposition: Proposition = cls.objects.get(pk=pk)
        return proposition.summary_link

    @classmethod
    def get_updated_placeholder(cls, match: Match) -> str:
        """Return a placeholder for a model instance depicted in an HTML field."""
        placeholder: str = str(match.group(0))
        logging.debug(f'Looking at {truncate(placeholder)}')
        extant_html: Optional[str] = (
            str(match.group(PlaceholderGroups.HTML)).strip()
            if match.group(PlaceholderGroups.HTML)
            else None
        )
        if extant_html:
            if '<a ' not in extant_html:
                html = cls.get_object_html(match)
                html = re.sub(
                    r'(.+?">).+?(<\/a>)',  # TODO
                    rf'\g<1>{extant_html}\g<2>',
                    html,
                )
                placeholder = placeholder.replace(
                    match.group(PlaceholderGroups.HTML), html
                )
            else:
                logging.info('Returning extant placeholder')
                return placeholder
        else:
            html = cls.get_object_html(match)
            model_name = match.group(PlaceholderGroups.MODEL_NAME)
            pk = match.group(PlaceholderGroups.PK)
            placeholder = f'[[ {model_name}: {pk}: {html} ]]'
        return dedupe_newlines(placeholder)


class Proposition(TypedProposition):
    """A proposition."""
