import logging
from typing import TYPE_CHECKING, Optional

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.template.defaultfilters import truncatechars_html
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from rest_framework.serializers import Serializer

from apps.collections.models import AbstractCollectionInclusion
from apps.dates.fields import HistoricDateTimeField
from apps.dates.structures import HistoricDateTime
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
from apps.topics.models.taggable import AbstractTopicRelation, TaggableModel, TagsField
from core.constants.strings import EMPTY_STRING
from core.fields.array_field import ArrayField
from core.fields.html_field import HTMLField
from core.fields.json_field import JSONField
from core.fields.m2m_foreign_key import ManyToManyForeignKey
from core.models.model_with_cache import store
from core.models.module import TypedModule

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.entities.models import Categorization

NAME_MAX_LENGTH: int = 100

TRUNCATED_DESCRIPTION_LENGTH: int = 250

PARTS_OF_SPEECH = (
    ('noun', 'noun'),
    ('adj', 'adjective'),
    ('any', 'noun / adjective'),
)


def get_entity_fk(related_name: str) -> ManyToManyForeignKey:
    """Return a foreign key field referencing an entity."""
    return ManyToManyForeignKey(
        to='entities.Entity',
        related_name=related_name,
        verbose_name='entity',
    )


class CollectionInclusion(AbstractCollectionInclusion):
    """An inclusion of an entity in a collection."""

    content_object = get_entity_fk(related_name='collection_inclusions')


class ImageRelation(AbstractImageRelation):
    """A relation of an image to an entity."""

    content_object = get_entity_fk(related_name='image_relations')


class QuoteRelation(AbstractQuoteRelation):
    """A relation of a quote to an entity."""

    content_object = get_entity_fk(related_name='quote_relations')


class TopicRelation(AbstractTopicRelation):
    """A relation of a topic to an entity."""

    content_object = get_entity_fk(related_name='topic_relations')


class EntityRelation(AbstractEntityRelation):
    """A relation of an entity to an entity."""

    content_object = get_entity_fk(related_name='entity_relations')


class Entity(
    TypedModule,
    ModelWithImages,
    ModelWithRelatedQuotes,
    ModelWithRelatedEntities,
    TaggableModel,
):
    """An entity."""

    name = models.CharField(
        verbose_name=_('name'),
        max_length=NAME_MAX_LENGTH,
        unique=True,
    )
    unabbreviated_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        blank=True,
    )
    aliases = ArrayField(
        models.CharField(max_length=NAME_MAX_LENGTH),
        verbose_name=_('aliases'),
        null=True,
        blank=True,
    )
    birth_date = HistoricDateTimeField(null=True, blank=True)
    death_date = HistoricDateTimeField(null=True, blank=True)
    birth = models.OneToOneField(
        to='propositions.Birth',
        on_delete=models.SET_NULL,
        related_name='born_entity',
        null=True,
        blank=True,
    )
    death = models.OneToOneField(
        to='propositions.Death',
        on_delete=models.SET_NULL,
        related_name='dead_entity',
        null=True,
        blank=True,
    )
    description = HTMLField(blank=True, paragraphed=True)
    categories = models.ManyToManyField(
        to='entities.Category',
        through='entities.Categorization',
        related_name='entities',
        blank=True,
    )
    images = ImagesField(through=ImageRelation)
    affiliated_entities = models.ManyToManyField(
        to='self', through='entities.Affiliation', blank=True
    )
    reference_urls = JSONField(blank=True, default=dict)
    related_quotes = RelatedQuotesField(through=QuoteRelation)
    related_entities = RelatedEntitiesField(through=EntityRelation)
    tags = TagsField(through=TopicRelation)

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        verbose_name_plural = 'Entities'
        ordering = ['name']

    searchable_fields = ['name', 'aliases', 'description']
    slug_base_fields = ('unabbreviated_name',)

    @classmethod
    def get_serializer(self):
        """Return the serializer for the entity."""
        from apps.entities.api.serializers import EntitySerializer

        return EntitySerializer

    def __str__(self) -> str:
        """Return the string representation of the entity."""
        return f'{self.name}'

    def clean(self):
        self.validate_type(raises=ValidationError)
        validate_url = URLValidator()
        for key, value in self.reference_urls.items():
            # TODO: refactor
            if key not in ('wikipedia',):
                raise ValidationError(f'{key} reference URL is unsupported.')
            validate_url(value)  # raises a ValidationError
        if not self.unabbreviated_name:
            self.unabbreviated_name = self.name
        super().clean()

    def get_default_title(self) -> str:
        """Return the value the title should be set to, if not manually set."""
        return self.unabbreviated_name

    @property
    def has_quotes(self) -> bool:
        """Return whether the entity has any attributed quotes."""
        return self.quotes.exists()

    @property
    def name_html(self) -> str:
        """Return an HTML string of the entity's name."""
        logging.debug(f'Getting name_html for {self}')
        return format_html(
            f'<span class="entity-name" data-entity-id="{self.pk}">{self.name}</span>'
        )

    @property
    def truncated_description(self) -> str:
        """Return the entity's description, truncated."""
        return format_html(
            truncatechars_html(self.description, TRUNCATED_DESCRIPTION_LENGTH)
            .replace('<p>', '')
            .replace('</p>', '')
        )

    def get_categorization(self, date: HistoricDateTime) -> Optional['Categorization']:
        """Return the most applicable categorization based on the date."""
        if not self.categories.exists():
            return None
        categorizations = self.categorizations.all()
        categorizations = categorizations.exclude(date__gt=date) if date else categorizations
        if not len(categorizations):
            categorizations = self.categorizations.all()
        return categorizations.order_by('date', 'category__weight').last()

    def get_categorizations(
        self, date: Optional[HistoricDateTime] = None
    ) -> 'QuerySet[Categorization]':
        """Return a list of all applicable categorizations."""
        categorizations = (
            self.categorizations.exclude(date__gt=date)
            if date
            else self.categorizations.all()
        )
        return categorizations.select_related('category')

    @store(key='categorization_string')
    def get_categorization_string(self, date: Optional[HistoricDateTime] = None) -> str:
        """Intelligently build a categorization string, like `liberal scholar`."""
        categorizations: 'QuerySet[Categorization]' = self.get_categorizations(date)
        if categorizations:
            # Build the string
            categorization_words: list[str] = []
            for part_of_speech in ('noun', 'any', 'adj'):
                pos_categorizations = categorizations.filter(
                    category__part_of_speech=part_of_speech
                )
                if pos_categorizations.exists():
                    categorization_str = str(
                        pos_categorizations.order_by('category__weight', 'date').last()
                    )
                    words = [
                        word
                        for word in categorization_str.split(' ')
                        if word not in categorization_words
                    ]
                    categorization_words = words + categorization_words
            # Remove duplicate words
            categorization_words = list(dict.fromkeys(categorization_words))
            return ' '.join(categorization_words)
        return EMPTY_STRING

    def validate_type(self, raises: type[Exception] = ValidationError):
        """Validate the entity's type."""
        if self.type == 'entities.entity' or not self.type:
            raise raises('Entity requires a type.')
        else:
            # Prevent a RuntimeError when saving a new publication
            self.recast(self.type)

    def get_date(self) -> Optional[HistoricDateTime]:
        """Date used for sorting search results."""
        return self.birth_date


class Person(Entity):
    """A person."""

    class Meta:
        """Meta options for the Person model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'People'


class Deity(Entity):
    """A deity."""

    class Meta:
        """Meta options for the Deity model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'Deities'


class Group(Entity):
    """A group of people."""

    class Meta:
        """Meta options for the Group model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'Groups'


class Organization(Entity):
    """An organization."""

    class Meta:
        """Meta options for the Organization model."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options

        verbose_name_plural = 'Organizations'

    @property
    def founding_date(self) -> HistoricDateTime:
        """Return the date the organization was founded."""
        return self.birth_date
