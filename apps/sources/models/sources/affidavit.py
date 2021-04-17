"""Model classes for affidavits (as sources)."""

from django.core.exceptions import ValidationError
from django.db import models

from apps.sources.models import Source
from apps.sources.models.mixins.document import DocumentMixin

NAME_MAX_LENGTH: int = 100


class Affidavit(Source, DocumentMixin):
    """An affidavit."""

    certifier = models.CharField(
        max_length=NAME_MAX_LENGTH,
        null=True,
        blank=True,
    )

    def clean(self):
        """Prepare the source to be saved."""
        super().clean()
        if not self.location:
            raise ValidationError('Affidavit needs a certification location.')

    def __html__(self) -> str:
        """Return the source's HTML representation."""
        if self.location:
            affidavit_string = (
                f'affidavit sworn {self.date_html} at {self.location.string} '
                f'before {self.certifier}'
            )
        else:
            affidavit_string = (
                f'affidavit sworn {self.date_html} before {self.certifier}'
            )
        components = [
            self.attributee_html,
            affidavit_string,
        ]
        return self.components_to_html(components)
