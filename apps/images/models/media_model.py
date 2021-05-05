from django.db import models

from apps.search.models.searchable_dated_model import SearchableDatedModel
from core.fields import HTMLField

PROVIDER_MAX_LENGTH: int = 200


class MediaModel(SearchableDatedModel):
    """Abstract base model for media models (e.g., images and videos)."""

    caption = HTMLField(null=True, blank=True, paragraphed=False)
    description = HTMLField(null=True, blank=True)
    provider = models.CharField(max_length=PROVIDER_MAX_LENGTH, null=True, blank=True)

    class Meta:
        """Meta options for MediaModel."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True

    class FieldNames(SearchableDatedModel.FieldNames):
        description = 'description'
        caption = 'caption'
        provider = 'provider'

    slug_base_field = FieldNames.caption
