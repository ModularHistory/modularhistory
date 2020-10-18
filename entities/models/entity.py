from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from django.db import models
from django.db.models import ForeignKey, ManyToManyField, QuerySet, SET_NULL
from django.template.defaultfilters import truncatechars_html
from django.utils.html import format_html
from django.utils.safestring import SafeString

from images.models import Image
from modularhistory.fields import ArrayField, HTMLField, HistoricDateTimeField
from modularhistory.models import (
    ModelWithImages,
    ModelWithRelatedEntities,
    ModelWithRelatedQuotes,
    TaggableModel,
    TypedModel
)
from modularhistory.structures import HistoricDateTime

if TYPE_CHECKING:
    from entities.models import Categorization

NAME_MAX_LENGTH: int = 100

TRUNCATED_DESCRIPTION_LENGTH: int = 1200

PARTS_OF_SPEECH = (
    ('noun', 'noun'),
    ('adj', 'adjective'),
    ('any', 'noun / adjective'),
)


class Entity(TypedModel, TaggableModel, ModelWithImages, ModelWithRelatedQuotes, ModelWithRelatedEntities):
    """An entity."""

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    unabbreviated_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        null=True,
        blank=True
    )
    aliases = ArrayField(
        models.CharField(max_length=NAME_MAX_LENGTH),
        null=True,
        blank=True
    )
    birth_date = HistoricDateTimeField(null=True, blank=True)
    death_date = HistoricDateTimeField(null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    categories = ManyToManyField(
        'entities.Category',
        through='entities.Categorization',
        related_name='entities',
        blank=True
    )
    images = ManyToManyField(
        Image,
        through='entities.EntityImage',
        related_name='entities',
        blank=True
    )
    affiliated_entities = ManyToManyField(
        'self',
        through='entities.Affiliation',
        blank=True
    )

    searchable_fields = ['name', 'aliases', 'description']

    class Meta:
        verbose_name_plural = 'Entities'
        ordering = ['name']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return f'{self.name}'

    @property
    def has_quotes(self) -> bool:
        """TODO: add docstring."""
        return bool(len(self.quotes.all()))

    @property
    def truncated_description(self) -> SafeString:
        """TODO: add docstring."""
        return format_html(truncatechars_html(self.description, TRUNCATED_DESCRIPTION_LENGTH))

    def clean(self):
        """TODO: add docstring."""
        super().clean()
        if not self.unabbreviated_name:
            self.unabbreviated_name = self.name

    def get_categorization(self, date: HistoricDateTime) -> Optional['Categorization']:
        """TODO: add docstring."""
        if not self.categories.exists():
            return None
        categorizations = self.categorizations.all()
        categorizations = categorizations.exclude(date__gt=date) if date else categorizations
        if not len(categorizations):
            categorizations = self.categorizations.all()
        return categorizations.order_by('date', 'category__weight').last()

    def get_categorizations(self, date: Optional[HistoricDateTime] = None) -> 'QuerySet[Categorization]':
        """Return a list of all applicable categorizations."""
        categorizations = self.categorizations.exclude(date__gt=date) if date else self.categorizations.all()
        return categorizations.select_related('category')

    def get_categorization_string(self, date: Optional[HistoricDateTime] = None) -> Optional[str]:
        """Intelligently build a categorization string, like `conservative LDS apostle`."""
        categorization_string = self.computations.get('categorization_string')
        if not categorization_string:
            categorizations: 'QuerySet[Categorization]' = self.get_categorizations(date)
            if not categorizations:
                return None
            # Build the string
            categorization_words: List[str] = []
            for part_of_speech in ('noun', 'any', 'adj'):
                pos_categorizations = categorizations.filter(category__part_of_speech=part_of_speech)
                if pos_categorizations.exists():
                    categorization_str = str(pos_categorizations.order_by('category__weight', 'date').last())
                    words = [word for word in categorization_str.split(' ') if word not in categorization_words]
                    categorization_words = words + categorization_words
            # Remove duplicate words
            categorization_words = list(dict.fromkeys(categorization_words))
            categorization_string = ' '.join(categorization_words)
            # TODO: update asynchronously
            self.computations['categorization_string'] = categorization_string
            self.save()
        return categorization_string

    def save(self, *args, **kwargs):
        """TODO: add docstring."""
        self.clean()
        super().save(*args, **kwargs)


class Person(Entity):
    """A person."""

    class Meta:
        verbose_name_plural = 'People'


class Deity(Entity):
    """A deity."""

    class Meta:
        verbose_name_plural = 'Deities'


class Group(Entity):
    """TODO: add docstring."""

    class Meta:
        verbose_name_plural = 'Groups'


class Organization(Entity):
    """An organization."""
    parent_organization = ForeignKey(
        'self',
        related_name='child_organizations',
        null=True, blank=True,
        on_delete=SET_NULL
    )

    class Meta:
        verbose_name_plural = 'Organizations'

    @property
    def founding_date(self) -> datetime:
        """TODO: add docstring."""
        return self.birth_date
