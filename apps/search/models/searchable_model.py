"""Base classes for models that appear in ModularHistory search results."""

import logging
import uuid
from typing import TYPE_CHECKING

import serpy
from autoslug import AutoSlugField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from apps.topics.models.taggable_model import TaggableModel
from apps.verifications.models import VerifiableModel
from modularhistory.models.model import ModelSerializer
from modularhistory.models.model_with_computations import ModelWithComputations
from modularhistory.utils.html import soupify

if TYPE_CHECKING:
    from apps.search.models.manager import SearchableModelManager


class SearchableModel(TaggableModel, ModelWithComputations, VerifiableModel):
    """
    A model that shows up in ModularHistory's search results; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but do to Django's model magic,
    it must be defined as an abstract model class.
    """

    key = models.UUIDField(
        verbose_name=_('key'),
        primary_key=False,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    slug = AutoSlugField(
        verbose_name=_('slug'),
        null=True,
        blank=True,
        editable=True,
        unique=True,
        db_index=True,
        populate_from='get_slug',
    )
    hidden = models.BooleanField(
        default=False,
        blank=True,
        help_text='Hide this item from search results.',
    )

    class FieldNames(TaggableModel.FieldNames):
        verified = 'verified'
        hidden = 'hidden'

    class Meta:
        abstract = True

    objects: 'SearchableModelManager'
    slug_base_field: str = 'key'

    @classmethod
    def from_db(cls, db, field_names, values):
        """Customize model instance creation when loading from the database."""
        instance: 'SearchableModel' = super().from_db(db, field_names, values)
        if not instance.slug:
            instance.slug = instance.get_slug()
        return instance

    def clean(self):
        """Prepare the model instance to be saved."""
        if not self.slug:
            self.slug = self.get_slug()
        super().clean()

    @property
    def absolute_url(self) -> str:
        """Return the URL for the model instance detail page."""
        return self.get_absolute_url()

    def get_absolute_url(self):
        """Return the URL for the model instance detail page."""
        absolute_url = ''
        if self.slug:
            absolute_url = reverse(
                f'{self.get_meta().app_label}:detail_slug', args=[str(self.slug)]
            )
        else:
            absolute_url = reverse(
                f'{self.get_meta().app_label}:detail', args=[str(self.pk)]
            )
        logging.debug(f'Determined absolute URL: {absolute_url}')
        return absolute_url

    def get_slug(self):
        """Get a slug for the model instance."""
        slug = None
        slug_base_field = getattr(self, 'slug_base_field', None)
        if slug_base_field:
            slug_base = str(getattr(self, slug_base_field, self.pk))
            if '<' in slug_base:
                slug_base = soupify(slug_base).get_text()
            slug = slugify(slug_base)
        return slug or self.pk


class SearchableModelSerializer(ModelSerializer):
    """Base serializer for searchable models."""

    slug = serpy.StrField()
    tags_html = serpy.StrField()
    absolute_url = serpy.StrField()
    verified = serpy.BoolField()
