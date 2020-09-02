# type: ignore
# TODO: remove above line after fixing typechecking
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from django.db import models
from django.db.models import ForeignKey, ManyToManyField, CASCADE, SET_NULL
from django.template.defaultfilters import truncatechars_html
from django.utils.safestring import SafeText, mark_safe

from history.fields import ArrayField, HistoricDateTimeField, HTMLField
from history.models import (
    Model, TaggableModel, TypedModel,
    RelatedQuotesMixin
)
from history.structures import HistoricDateTime
from images.models import Image

if TYPE_CHECKING:
    from entities.models import Categorization


class EntityImage(Model):
    """TODO: add docstring."""

    entity = ForeignKey('Entity', related_name='entity_images', on_delete=CASCADE)
    image = ForeignKey(Image, related_name='image_entities', on_delete=CASCADE)

    class Meta:
        unique_together = ['entity', 'image']

    def __str__(self) -> str:
        """TODO: write docstring."""
        return f'{self.image} ({self.image.id}) --> {self.entity} ({self.entity.id})'


parts_of_speech = (
    ('noun', 'noun'),
    ('adj', 'adjective'),
    ('any', 'noun / adjective'),
)


class Entity(TypedModel, TaggableModel, RelatedQuotesMixin):
    """An entity."""

    NAME_MAX_LENGTH: int = 100

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    verbose_name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True, null=True, blank=True)
    aliases = ArrayField(
        models.CharField(max_length=NAME_MAX_LENGTH),
        null=True, blank=True
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
    def image(self) -> Optional[Image]:
        """TODO: add docstring."""
        return (self.images.first() if self.images.exists()
                else None)

    @property
    def has_quotes(self) -> bool:
        """TODO: add docstring."""
        return bool(len(self.quotes.all()))

    @property
    def description__truncated(self) -> SafeText:
        """TODO: add docstring."""
        return mark_safe(truncatechars_html(self.description, 1200))

    def clean(self):
        """TODO: add docstring."""
        super().clean()
        if not self.verbose_name:
            self.verbose_name = self.name

    def get_categorization(self, date: HistoricDateTime) -> Optional['Categorization']:
        """TODO: add docstring."""
        if not self.categories.exists():
            return None
        categorizations = self.categorizations.all()
        categorizations = categorizations.exclude(date__gt=date) if date else categorizations
        if not len(categorizations):
            categorizations = self.categorizations.all()
        categorization = categorizations.order_by('date', 'category__weight').last()
        return categorization

    def get_categorization_string(
            self, date: HistoricDateTime
    ) -> Optional[str]:
        """Intelligently build a categorization string, like `conservative LDS apostle`."""
        if not self.categories.exists():
            return None
        words = []
        categorizations = self.categorizations.all()
        categorizations = categorizations.exclude(date__gt=date) if date else categorizations

        noun_categorizations = categorizations.filter(category__part_of_speech='noun')
        if noun_categorizations.exists():
            noun = noun_categorizations.order_by('category__weight', 'date').last()
            words += str(noun).split(' ')

        noun_adj_categorizations = categorizations.filter(category__part_of_speech='any')
        if noun_adj_categorizations.exists():
            noun_adj = noun_adj_categorizations.order_by('category__weight', 'date').last()
            words = [word for word in str(noun_adj).split(' ') if word not in words] + words

        adj_categorizations = categorizations.filter(category__part_of_speech='adj')
        if adj_categorizations.exists():
            adj = adj_categorizations.order_by('category__weight', 'date').last()
            words = [word for word in str(adj).split(' ') if word not in words] + words

        # Final removal of duplicate words
        words = list(dict.fromkeys(words))
        return ' '.join(words)

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

    pass


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
