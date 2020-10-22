from django.db import models

from modularhistory.fields import HTMLField
from modularhistory.models import DatedModel, SearchableModel

PROVIDER_MAX_LENGTH: int = 200


class MediaModel(DatedModel, SearchableModel):
    """Abstract base model for media models (e.g., images and videos)."""

    caption = HTMLField(null=True, blank=True)
    description = HTMLField(null=True, blank=True)
    provider = models.CharField(max_length=PROVIDER_MAX_LENGTH, null=True, blank=True)

    class Meta:
        abstract = True
