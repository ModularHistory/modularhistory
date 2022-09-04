"""Model classes for books and sections/chapters (as sources)."""

from typing import Optional

from django.db import models
from django.utils.translation import ugettext_lazy as _
from humanize import ordinal

from apps.sources.models.mixins.textual import TextualMixin
from apps.sources.models.source import Source
from core.constants.strings import EMPTY_STRING


class Book(Source, TextualMixin):
    """A book."""

    translator = models.CharField(
        max_length=100,
        blank=True,
    )
    publisher = models.CharField(
        max_length=100,
        blank=True,
    )
    edition_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    edition_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    printing_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    volume_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    @property
    def edition_string(self) -> Optional[str]:
        """Return a string representation of the book's edition, if it has one."""
        if self.edition_number:
            edition_string = f'{ordinal(self.edition_number)} edition'
            if self.edition_year:
                edition_string = f'{edition_string} ({self.edition_year})'
        elif self.has_edition_year:
            edition_year = self.edition_year or self.date.year
            edition_string = f'{edition_year} edition'
            if self.original_publication_date:
                edition_string = (
                    f'{edition_string} (orig. {self.original_publication_date.year})'
                )
        else:
            return None
        return edition_string

    def get_original_publication_date(self):
        """Return the book's original publication date."""
        return (
            self.original_edition.date
            if self.original_edition
            else self.original_publication_date
        )

    @property
    def has_edition_year(self) -> bool:
        """Return True if an edition year can be determined for the book, else False."""
        return bool(
            self.edition_year
            or (self.get_original_publication_date() and not self.edition_number)
        )

    @property
    def has_printing(self) -> bool:
        """Return True if a printing (distinct from edition) can be determined."""
        has_printing = (
            self.get_original_publication_date()
            and self.printing_number
            and not self.edition_number
        )
        if has_printing:
            return True
        elif self.edition_year and int(self.edition_year) < self.date.year:
            return True
        return False

    @property
    def printing_string(self) -> Optional[str]:
        """Return a string representation of the book's printing, if it has one."""
        has_printing_year = self.has_printing
        if self.printing_number and not has_printing_year:
            return f'{ordinal(self.printing_number)} printing'
        elif has_printing_year:
            printing_year_string = f'{self.date.year} printing'
            if self.original_publication_date:
                printing_year_string = (
                    f'{printing_year_string} '
                    f'(orig. {self.original_publication_date.year})'
                )
            return printing_year_string
        return None

    def __html__(self) -> str:
        """Return the book's citation HTML string."""
        components = [
            self.attributee_html if self.attributee_html else EMPTY_STRING,
            f'<i>{self.linked_title}</i>' if self.title else EMPTY_STRING,
            self.edition_string,
            self.printing_string,
            f'ed. {self.editors}' if self.editors else EMPTY_STRING,
            f'translated by {self.translator}' if self.translator else EMPTY_STRING,
            f'{self.publisher}' if self.publisher else EMPTY_STRING,
            f'vol. {self.volume_number}' if self.volume_number else EMPTY_STRING,
        ]
        if self.date and not self.has_edition_year and not self.has_printing:
            components.append(f'{self.date.year}')
        return self.components_to_html(components)


SECTION_TYPES = (
    ('chapter', 'Chapter'),
    ('section', 'Section'),
)


class Section(Source):
    """A section or chapter of a book."""

    type = models.CharField(
        verbose_name=_('section type'),
        max_length=10,
        choices=SECTION_TYPES,
        default=SECTION_TYPES[0][0],
    )

    # `book` would clash with the 1-to-1 reverse accessor of Source.
    work = models.ForeignKey(to='sources.Book', on_delete=models.CASCADE)

    def __html__(self) -> str:
        """Return the section/chapter's HTML representation."""
        components = [
            self.attributee_html if self.attributee_html else EMPTY_STRING,
            f'"{self.linked_title}"' if self.title else EMPTY_STRING,
            self.work.citation_html.replace(self.attributee_html, '').lstrip(', '),
        ]
        return self.components_to_html(components)

    def clean(self):
        """Prepare the section to be saved."""
        if self.work and not self.date:
            self.date = self.work.date
        super().clean()
