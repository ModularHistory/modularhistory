"""Base classes for models that appear in ModularHistory search results."""

from typing import TYPE_CHECKING

from django.db import models

from apps.topics.models.taggable_model import TaggableModel
from apps.verifications.models import VerifiableModel
from core.models.slugged_model import SluggedModel

if TYPE_CHECKING:
    from apps.search.models.manager import SearchableModelManager


class SearchableModel(SluggedModel, TaggableModel, VerifiableModel):
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
