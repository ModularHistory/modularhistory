from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models.mixins.page_numbers import PageNumbersMixin
from apps.sources.models.source import Source

PIECE_TYPES = (('essay', 'Essay'),)
TYPE_MAX_LENGTH: int = 10


class Piece(Source, PageNumbersMixin):
    """A piece (e.g., essay)."""

    type = models.CharField(
        verbose_name=_('piece type'),
        max_length=TYPE_MAX_LENGTH,
        choices=PIECE_TYPES,
        default=PIECE_TYPES[0][0],
    )

    def __html__(self) -> str:
        """Return the piece's citation HTML string."""
        components = [
            self.attributee_html,
            f'"{self.linked_title}"',
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)
