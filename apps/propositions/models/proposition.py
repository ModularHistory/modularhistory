import logging
import re
from typing import TYPE_CHECKING, Match, Optional, Union

from bs4.element import NavigableString, Tag
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import truncatechars_html
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.collections.models import AbstractCollectionInclusion
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
from apps.places.models.model_with_locations import (
    AbstractLocationRelation,
    LocationsField,
    ModelWithLocations,
)
from apps.propositions.serializers import PropositionSerializer
from apps.quotes.models.model_with_related_quotes import (
    AbstractQuoteRelation,
    ModelWithRelatedQuotes,
    RelatedQuotesField,
)
from apps.sources.models.citation import AbstractCitation
from apps.sources.models.model_with_sources import ModelWithSources, SourcesField
from apps.topics.models.taggable import AbstractTopicRelation, TaggableModel, TagsField
from core.fields.html_field import (
    OBJECT_PLACEHOLDER_REGEX,
    TYPE_GROUP,
    HTMLField,
    PlaceholderGroups,
)
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.manager import SearchableManager
from core.models.model_with_cache import store
from core.models.module import Module
from core.utils.html import escape_quotes, soupify
from core.utils.string import dedupe_newlines, truncate

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from django.db.models.query import QuerySet

    from apps.entities.models.entity import Entity
    from apps.images.models.image import Image
    from apps.propositions.models.argument import Argument


TRUNCATED_DESCRIPTION_LENGTH: int = 250
proposition_placeholder_regex = OBJECT_PLACEHOLDER_REGEX.replace(
    TYPE_GROUP, rf'(?P<{PlaceholderGroups.MODEL_NAME}>proposition)'  # noqa: WPS360
)
logging.debug(f'Proposition placeholder pattern: {proposition_placeholder_regex}')


DEGREES_OF_CERTAINTY = (
    (None, '-------'),
    (0, 'No credible evidence'),
    (1, 'Some credible evidence'),
    (2, 'A preponderance of evidence'),
    (3, 'Beyond reasonable doubt'),
    (4, 'Beyond any shadow of a doubt'),
)


def get_proposition_fk(related_name: str) -> ManyToManyForeignKey:
    """Return a foreign key field referencing a proposition."""
    return ManyToManyForeignKey(
        to='propositions.Proposition',
        related_name=related_name,
        verbose_name='proposition',
    )


class CollectionInclusion(AbstractCollectionInclusion):
    """An inclusion of a proposition in a collection."""

    content_object = get_proposition_fk(related_name='collection_inclusions')


class Citation(AbstractCitation):
    """A relation of a source to a proposition."""

    content_object = get_proposition_fk(related_name='citations')


class Location(AbstractLocationRelation):
    """A relation of a location to a proposition."""

    content_object = get_proposition_fk(related_name='location_relations')


class ImageRelation(AbstractImageRelation):
    """A relation of an image to a proposition."""

    content_object = get_proposition_fk(related_name='image_relations')


class QuoteRelation(AbstractQuoteRelation):
    """A relation of a quote to a proposition."""

    content_object = get_proposition_fk(related_name='quote_relations')


class EntityRelation(AbstractEntityRelation):
    """A relation of an entity to a proposition."""

    content_object = get_proposition_fk(related_name='entity_relations')


class TopicRelation(AbstractTopicRelation):
    """A relation of a topic to a proposition."""

    content_object = get_proposition_fk(related_name='topic_relations')


TYPE_CHOICES = (
    ('propositions.conclusion', 'conclusion'),
    ('propositions.occurrence', 'occurrence'),
    ('propositions.birth', 'birth'),
    ('propositions.death', 'death'),
    ('propositions.publication', 'publication'),
    ('composition', 'Composition'),
    ('speech', 'Speech'),
)


class OccurrenceType(models.TextChoices):
    """Types of occurrences."""

    OCCURRENCE = 'occurrence', _('Occurrence')
    BIRTH = 'birth', _('Birth')
    DEATH = 'death', _('Death')
    SPEECH = 'speech', _('Speech')
    COMPOSITION = 'composition', _('Composition')
    PUBLICATION = 'publication', _('Publication')


class Proposition(  # noqa: WPS215
    Module,
    TaggableModel,
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
    arguments: 'RelatedManager[Argument]'
    conflicting_propositions = models.ManyToManyField(
        to='self',
        symmetrical=True,
        through='propositions.Conflict',
        verbose_name=_('conflicting propositions'),
    )

    sources = SourcesField(
        through=Citation,
        related_name='propositions',
    )

    images = ImagesField(through=ImageRelation)
    locations = LocationsField(through=Location)
    related_quotes = RelatedQuotesField(
        through=QuoteRelation,
        related_name='propositions',
    )
    related_entities = RelatedEntitiesField(through=EntityRelation)
    tags = TagsField(through=TopicRelation)

    postscript = HTMLField(
        verbose_name=_('postscript'),
        blank=True,
        paragraphed=True,
        help_text='Content to be displayed below all related data',
    )

    searchable_fields = [
        'title',
        'summary',
        'tags__name',
        'elaboration',
        'related_entities__name',
        'related_entities__aliases',
        'tags__aliases',
    ]
    serializer = PropositionSerializer
    slug_base_fields = ('title', 'summary')

    def __str__(self) -> str:
        """Return the proposition's string representation."""
        return self.summary

    def clean(self):
        if self.type == 'propositions.occurrence' and not self.date:
            raise ValidationError('Occurrence needs a date.')
        elif self.type == 'propositions.proposition' and not self.certainty:
            raise ValidationError('Proposition needs a degree of certainty.')
        super().clean()

    def post_save(self):
        super().post_save()
        if not self.images.exists():
            image: Optional['Image'] = None
            if self.related_entities.exists():
                entity: 'Entity'
                for entity in self.related_entities.all():
                    if entity.images.exists():
                        if self.date:
                            image = entity.images.get_closest_to_datetime(self.date)
                        else:
                            image = entity.image
            if image:
                self.images.add(image)

    @property
    @store
    def truncated_elaboration(self) -> Optional[SafeString]:
        """Return the occurrence's elaboration, truncated."""
        if not self.elaboration:
            return None
        elaboration_soup = soupify(self.elaboration, features='html.parser')
        img_tag: Optional[Union[Tag, NavigableString]] = elaboration_soup.find('img')
        if isinstance(img_tag, Tag):
            img_tag.decompose()
        truncated_elaboration = (
            truncatechars_html(elaboration_soup.prettify(), TRUNCATED_DESCRIPTION_LENGTH)
            .replace('<p>', '')
            .replace('</p>', '')
            .strip('\n')
        )
        return format_html(truncated_elaboration)

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

    def get_default_title(self) -> str:
        """Return the value the title should be set to, if not manually set."""
        return self.summary

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


class ConclusionManager(SearchableManager):
    """Manager for propositions."""

    def get_queryset(self) -> 'QuerySet':
        """Return the propositions of type `propositions.proposition`."""
        return super().get_queryset().filter(type='propositions.conclusion')


class Conclusion(Proposition):
    """A proposition."""

    class Meta:
        proxy = True

    objects = ConclusionManager()
