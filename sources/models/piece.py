from bs4 import BeautifulSoup
from django.db import models

from sources.models.source import OldTitledSource
from sources.models.source_with_page_numbers import OldSourceWithPageNumbers, SourceWithPageNumbers

TYPE_MAX_LENGTH: int = 10

PIECE_TYPES = (
    ('essay', 'Essay'),
)


class OldPiece(OldTitledSource, OldSourceWithPageNumbers):
    """TODO: add docstring."""

    type2 = models.CharField(max_length=TYPE_MAX_LENGTH, choices=PIECE_TYPES, default='essay')

    def __str__(self) -> str:
        """TODO: add docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        components = [
            self.attributee_string,
            f'"{self.linked_title}"',
            self.date.string if self.date else ''
        ]
        # Remove blank values
        components = [component for component in components if component]
        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')


class Piece(SourceWithPageNumbers):
    """A piece (e.g., essay)."""

    def __str__(self) -> str:
        """TODO: add docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """TODO: write docstring."""
        components = [
            self.attributee_string,
            f'"{self.linked_title}"',
            self.date.string if self.date else ''
        ]
        # Remove blank values
        components = [component for component in components if component]
        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')


class Essay(Piece):
    """An essay (as a source)."""

    pass
