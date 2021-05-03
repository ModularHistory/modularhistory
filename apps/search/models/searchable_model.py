"""Base classes for models that appear in ModularHistory search results."""

import uuid
from typing import TYPE_CHECKING

import serpy
from autoslug import AutoSlugField
from django.db import models
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

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True

    objects: 'SearchableModelManager'
    slug_base_field: str = 'key'

    def clean(self):
        """Prepare the model instance to be saved."""
        if not self.slug:
            self.slug = self.get_slug()
        super().clean()


class SearchableModelSerializer(ModelSerializer):
    """Base serializer for searchable models."""

    absoluteUrl = serpy.StrField(attr='absolute_url')
    adminUrl = serpy.StrField(attr='admin_url')
    slug = serpy.StrField()
    tagsHtml = serpy.StrField(attr='tags_html')
    title = serpy.StrField()
    verified = serpy.BoolField()
