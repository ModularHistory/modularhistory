from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.sources.models import PolymorphicSource

from .source_with_page_numbers import PageNumbersMixin, SourceWithPageNumbers

PIECE_TYPES = (('essay', 'Essay'),)
TYPE_MAX_LENGTH: int = 10


class PolymorphicPiece(PolymorphicSource, PageNumbersMixin):
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


class Piece(SourceWithPageNumbers):
    """A piece (e.g., essay)."""

    def __html__(self) -> str:
        """TODO: write docstring."""
        components = [
            self.attributee_html,
            f'"{self.linked_title}"',
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)


class Essay(Piece):
    """An essay (as a source)."""

    pass  # noqa: WPS604
