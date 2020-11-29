"""Base classes for models that appear in ModularHistory search results."""

import uuid
from typing import TYPE_CHECKING
import logging
import serpy
from autoslug import AutoSlugField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from modularhistory.models.model import ModelSerializer
from modularhistory.models.model_with_computations import ModelWithComputations
from topics.models.taggable_model import TaggableModel
from verifications.models import VerifiableModel

if TYPE_CHECKING:
    from search.models.manager import SearchableModelManager


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
        db_index=True,
        editable=True,
        null=True,
        populate_from='get_slug',
        unique=True,
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

    def clean(self):
        """Prepare the model instance to be saved."""
        super().clean()
        if not self.slug:
            self.slug = self.get_slug()

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
        logging.info(f'Absolute URL: {absolute_url}')
        return absolute_url

    def get_slug(self):
        """Get a slug for the model instance."""
        slug = None
        slug_base_field = getattr(self, 'slug_base_field', None)
        if slug_base_field:
            slug = slugify(getattr(self, slug_base_field, self.pk))
        return slug or self.pk


class SearchableModelSerializer(ModelSerializer):
    """Base serializer for searchable models."""

    key = serpy.StrField()
    tags_html = serpy.Field()
    absolute_url = serpy.Field()
