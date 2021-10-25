from django.db import models

from apps.dates.models import DatedModel
from apps.topics.models.taggable import TaggableModel
from core.fields.html_field import HTMLField
from core.models.module import Module

PROVIDER_MAX_LENGTH: int = 200


class MediaModel(Module, TaggableModel, DatedModel):
    """Abstract base model for media models (e.g., images and videos)."""

    caption = HTMLField(paragraphed=False)
    description = HTMLField(blank=True)
    provider = models.CharField(max_length=PROVIDER_MAX_LENGTH, blank=True)

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    slug_base_fields = ('title', 'caption')

    def get_default_title(self) -> str:
        """Return the value the title should be set to, if not manually set."""
        return self.caption

    @property
    def caption_html(self) -> str:
        """Return the user-facing caption HTML."""
        return self.caption

    @property
    def description_html(self) -> str:
        """Return the user-facing caption HTML."""
        return self.description
