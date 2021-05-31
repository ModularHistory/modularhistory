import logging
import re
from typing import TYPE_CHECKING, Match, Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Manager
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.dates.models import DatedModel
from apps.entities.models.model_with_related_entities import ModelWithRelatedEntities
from apps.images.models.model_with_images import ModelWithImages
from apps.places.models.model_with_locations import (
    AbstractLocationRelation,
    LocationsField,
    ModelWithLocations,
)
from apps.propositions.api.serializers import PropositionSerializer
from apps.quotes.models.model_with_related_quotes import (
    AbstractQuoteRelation,
    ModelWithRelatedQuotes,
    RelatedQuotesField,
)
from apps.search.models import SearchableModel
from apps.sources.models.citation import AbstractCitation
from apps.sources.models.model_with_sources import ModelWithSources, SourcesField
from core.fields.html_field import (
    OBJECT_PLACEHOLDER_REGEX,
    TYPE_GROUP,
    HTMLField,
    PlaceholderGroups,
)
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.utils.html import escape_quotes
from core.utils.string import dedupe_newlines, truncate

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.db.models.manager import RelatedManager

    from apps.propositions.models.argument import Argument


proposition_placeholder_regex = OBJECT_PLACEHOLDER_REGEX.replace(
    TYPE_GROUP, rf'(?P<{PlaceholderGroups.MODEL_NAME}>proposition)'  # noqa: WPS360
)
logging.debug(f'Proposition placeholder pattern: {proposition_placeholder_regex}')


DEGREES_OF_CERTAINTY = (
    (None, '-------'),
    (1, 'Some credible evidence'),
    (2, 'A preponderance of evidence'),
    (3, 'Beyond reasonable doubt'),
    (4, 'Beyond any shadow of a doubt'),
)


def get_proposition_fk(related_name: str) -> ManyToManyForeignKey:
    """Return a foreign key field referencing a proposition."""
    return ManyToManyForeignKey(
        to='propositions.PolymorphicProposition',
        related_name=related_name,
        verbose_name='proposition',
    )


class Citation(AbstractCitation):
    """A relationship between a proposition and a source."""

    content_object = get_proposition_fk(related_name='citations')


class Location(AbstractLocationRelation):
    """A relationship between a proposition and a place."""

    content_object = get_proposition_fk(related_name='location_relations')


class QuoteRelation(AbstractQuoteRelation):
    """A relationship between a proposition and a quote."""

    content_object = get_proposition_fk(related_name='quote_relations')


TYPE_CHOICES = (
    ('propositions.proposition', 'proposition'),
    ('propositions.occurrence', 'occurrence'),
    ('propositions.birth', 'birth'),
    ('propositions.death', 'death'),
    ('propositions.publication', 'publication'),
    ('propositions.verbalization', 'verbalization'),
)


class PolymorphicProposition(  # noqa: WPS215
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

    type = models.CharField(
        choices=TYPE_CHOICES,
        db_index=True,
        max_length=100,
    )
    summary = HTMLField(
        verbose_name=_('summary'),
        unique=True,
        paragraphed=False,
        processed=False,
    )
    elaboration = HTMLField(
        verbose_name=_('elaboration'),
        paragraphed=True,
    )
    certainty = models.PositiveSmallIntegerField(
        verbose_name=_('certainty'),
        null=True,
        blank=True,
        choices=DEGREES_OF_CERTAINTY,
    )
    postscript = HTMLField(
        verbose_name=_('postscript'),
        blank=True,
        paragraphed=True,
        help_text='Content to be displayed below all related data',
    )
    arguments: 'RelatedManager[Argument]'
    premises = models.ManyToManyField(
        to='self',
        through='propositions.Support',
        through_fields=('conclusion', 'premise'),
        related_name='conclusions',
        symmetrical=False,
        verbose_name=_('premises'),
    )

    locations = LocationsField(through=Location)
    related_quotes = RelatedQuotesField(
        through=QuoteRelation,
        related_name='propositions',
    )
    sources = SourcesField(
        through=Citation,
        related_name='propositions',
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
    slug_base_fields = ('title', 'summary')

    def __str__(self) -> str:
        """Return the proposition's string representation."""
        return self.summary

    def clean(self):
        """Prepare the proposition to be saved to the database."""
        if self.type == 'propositions.occurrence' and not self.date:
            raise ValidationError('Occurrence needs a date.')
        elif self.type == 'propositions.proposition' and not self.certainty:
            raise ValidationError('Proposition needs a degree of certainty.')
        super().clean()

    @property
    def escaped_summary(self) -> SafeString:
        """Return the escaped summary (for display in the Django admin)."""
        return format_html(self.summary)

    @property
    def summary_link(self) -> str:
        """Return an HTML link to the proposition, containing the summary text."""
        add_elaboration_tooltip = False
        elaboration = self.elaboration or ''
        elaboration = elaboration.replace('\n', '')
        if add_elaboration_tooltip:
            summary_link = (
                f'<a href="{reverse("propositions:detail", args=[self.pk])}"'
                ' class="proposition-link" target="_blank" '
                f'title="{escape_quotes(elaboration)}" '
                f'data-toggle="tooltip" data-html="true">{self.summary}'
                '</a>'
            )
        else:
            summary_link = (
                f'<a href="{reverse("propositions:detail", args=[self.pk])}"'
                ' class="proposition-link" target="_blank">'
                f'{self.summary}'
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
                placeholder = placeholder.replace(match.group(PlaceholderGroups.HTML), html)
            else:
                logging.info('Returning extant placeholder')
                return placeholder
        else:
            html = cls.get_object_html(match)
            model_name = match.group(PlaceholderGroups.MODEL_NAME)
            pk = match.group(PlaceholderGroups.PK)
            placeholder = f'[[ {model_name}: {pk}: {html} ]]'
        return dedupe_newlines(placeholder)


class PropositionManager(Manager):
    """Manager for propositions."""

    def get_queryset(self) -> 'QuerySet':
        """Return the propositions of type `propositions.proposition`."""
        return super().get_queryset().filter(type='propositions.proposition')


class Proposition(PolymorphicProposition):
    """A proposition."""

    class Meta:
        proxy = True

    objects = PropositionManager()
