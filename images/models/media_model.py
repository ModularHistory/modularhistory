from django.db import models

from modularhistory.fields import HTMLField
from search.models.searchable_dated_model import SearchableDatedModel

PROVIDER_MAX_LENGTH: int = 200


class MediaModel(SearchableDatedModel):
    """Abstract base model for media models (e.g., images and videos)."""

    caption = HTMLField(null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    provider = models.CharField(max_length=PROVIDER_MAX_LENGTH, null=True, blank=True)

    class Meta:
        """
        Meta options for MediaModel.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        abstract = True

    class FieldNames(SearchableDatedModel.FieldNames):
        description = 'description'
        caption = 'caption'
        provider = 'provider'

    slug_base_field = FieldNames.caption
