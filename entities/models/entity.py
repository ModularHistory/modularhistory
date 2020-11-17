import logging
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from django.db import models
from django.db.models import ForeignKey, ManyToManyField, QuerySet, SET_NULL
from django.template.defaultfilters import truncatechars_html
from django.utils.html import format_html

from entities.serializers import EntitySerializer
from modularhistory.constants.strings import EMPTY_STRING
from modularhistory.fields import ArrayField, HTMLField, HistoricDateTimeField
from modularhistory.models import (
    ModelWithComputations,
    ModelWithImages,
    ModelWithRelatedEntities,
    ModelWithRelatedQuotes,
    TaggableModel,
    TypedModel,
    retrieve_or_compute,
)
from modularhistory.structures import HistoricDateTime as DateTime

if TYPE_CHECKING:
    from entities.models import Categorization

NAME_MAX_LENGTH: int = 100

TRUNCATED_DESCRIPTION_LENGTH: int = 1200

PARTS_OF_SPEECH = (
    ('noun', 'noun'),
    ('adj', 'adjective'),
    ('any', 'noun / adjective'),
)


class Entity(
    TypedModel,
    TaggableModel,
    ModelWithComputations,
    ModelWithImages,
    ModelWithRelatedQuotes,
    ModelWithRelatedEntities,
):
    """An entity."""

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    unabbreviated_name = models.CharField(
        max_length=NAME_MAX_LENGTH, unique=True, null=True, blank=True
    )
    aliases = ArrayField(
        models.CharField(max_length=NAME_MAX_LENGTH), null=True, blank=True
    )
    birth_date = HistoricDateTimeField(null=True, blank=True)
    death_date = HistoricDateTimeField(null=True, blank=True)
    description = HTMLField(null=True, blank=True, paragraphed=True)
    categories = ManyToManyField(
        'entities.Category',
        through='entities.Categorization',
        related_name='entities',
        blank=True,
    )
    images = ManyToManyField(
        'images.Image',
        through='entities.EntityImage',
        related_name='entities',
        blank=True,
    )
    affiliated_entities = ManyToManyField(
        'self', through='entities.Affiliation', blank=True
    )

    class Meta:
        """
        Meta options for the Entity model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        verbose_name_plural = 'Entities'
        ordering = ['name']

    searchable_fields = ['name', 'aliases', 'description']
    serializer = EntitySerializer

    def __str__(self) -> str:
        """Return the string representation of the entity."""
        return f'{self.name}'

    def save(self, *args, **kwargs):
        """Save the entity to the database."""
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """Prepare the entity to be saved."""
        super().clean()
        if not self.unabbreviated_name:
            self.unabbreviated_name = self.name

    @property
    def has_quotes(self) -> bool:
        """Return whether the entity has any attributed quotes."""
        return bool(len(self.quotes.all()))

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
        )

    def get_categorization(self, date: DateTime) -> Optional['Categorization']:
        """Return the most applicable categorization based on the date."""
        if not self.categories.exists():
            return None
        categorizations = self.categorizations.all()
        categorizations = (
            categorizations.exclude(date__gt=date) if date else categorizations
        )
        if not len(categorizations):
            categorizations = self.categorizations.all()
        return categorizations.order_by('date', 'category__weight').last()

    def get_categorizations(
        self, date: Optional[DateTime] = None
    ) -> 'QuerySet[Categorization]':
        """Return a list of all applicable categorizations."""
        categorizations = (
            self.categorizations.exclude(date__gt=date)
            if date
            else self.categorizations.all()
        )
        return categorizations.select_related('category')

    @retrieve_or_compute(attribute_name='categorization_string')
    def get_categorization_string(self, date: Optional[DateTime] = None) -> str:
        """Intelligently build a categorization string, like `liberal scholar`."""
        categorizations: 'QuerySet[Categorization]' = self.get_categorizations(date)
        if categorizations:
            # Build the string
            categorization_words: List[str] = []
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


class Person(Entity):
    """A person."""

    class Meta:
        """
        Meta options for the Person model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        verbose_name_plural = 'People'


class Deity(Entity):
    """A deity."""

    class Meta:
        """
        Meta options for the Deity model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        verbose_name_plural = 'Deities'


class Group(Entity):
    """A group of people."""

    class Meta:
        """
        Meta options for the Group model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        verbose_name_plural = 'Groups'


class Organization(Entity):
    """An organization."""

    parent_organization = ForeignKey(
        'self',
        related_name='child_organizations',
        null=True,
        blank=True,
        on_delete=SET_NULL,
    )

    class Meta:
        """
        Meta options for the Organization model.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        verbose_name_plural = 'Organizations'

    @property
    def founding_date(self) -> datetime:
        """Return the date the organization was founded."""
        return self.birth_date
