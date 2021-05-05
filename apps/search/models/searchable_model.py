"""Base classes for models that appear in ModularHistory search results."""

import logging
import uuid
from typing import TYPE_CHECKING, Optional

import serpy
from autoslug import AutoSlugField
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from apps.topics.models.taggable_model import TaggableModel
from apps.verifications.models import VerifiableModel
from core.models.model import ModelSerializer
from core.models.model_with_computations import ModelWithComputations
from core.models.slugged_model import SluggedModel

if TYPE_CHECKING:
    from apps.search.models.manager import SearchableModelManager


class SearchableModel(
    SluggedModel, TaggableModel, ModelWithComputations, VerifiableModel
):
    """
    A model that shows up in ModularHistory's search results; e.g., a quote or occurrence.

    Ideally, this class would be a mixin, but due to Django's model magic,
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
        """Meta options for SearchableModel."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.

        abstract = True

    objects: 'SearchableModelManager'
    slug_base_field: str = 'key'

    def clean(self):
        """Prepare the model instance to be saved."""
        if not self.slug:
            self.slug = self.get_slug()
        super().clean()

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


ELASTICSEARCH_META_FIELDS_TO_CLEAN = ['id', 'index', 'doc_type']


class SearchableModelSerializer(ModelSerializer):
    """Base serializer for searchable models."""

    absolute_url = serpy.StrField()
    admin_url = serpy.StrField()
    slug = serpy.StrField()
    tags_html = serpy.StrField()
    title = serpy.StrField()
    verified = serpy.BoolField()
    meta = serpy.MethodField()

    def get_meta(self, model) -> Optional[dict]:
        if not hasattr(model, 'meta'):
            return None

        meta = model.meta.to_dict()
        for key in ELASTICSEARCH_META_FIELDS_TO_CLEAN:
            del meta[key]
        return model.meta.to_dict()
