"""Base classes for models that appear in ModularHistory search results."""

from typing import TYPE_CHECKING, Optional

import serpy
from django.db import models

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


ELASTICSEARCH_META_FIELDS_TO_CLEAN = ['id', 'index', 'doc_type']


class SearchableModelSerializer(ModelSerializer):
    """Base serializer for searchable models."""

    absoluteUrl = serpy.StrField(attr='absolute_url')
    adminUrl = serpy.StrField(attr='admin_url')
    slug = serpy.StrField()
    tagsHtml = serpy.StrField(attr='tags_html')
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
