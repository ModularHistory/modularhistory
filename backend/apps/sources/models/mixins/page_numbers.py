from typing import Optional

from django.db import models

from apps.sources.models.mixins.textual import TextualMixin

TYPE_MAX_LENGTH: int = 10


class PageNumbersMixin(TextualMixin):
    """Mixin for source models with page numbers."""

    page_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    end_page_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        """Meta options."""

        # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
        abstract = True

    @property
    def file_page_number(self) -> Optional[int]:
        """Return the page number to use for opening the source's associated file."""
        file = self.file
        if file:
            if self.page_number:
                return self.page_number + file.page_offset
            elif self.containment and self.containment.page_number:
                return self.containment.page_number + file.page_offset
        return None
