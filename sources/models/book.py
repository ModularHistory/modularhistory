"""Model classes for books and sections/chapters (as sources)."""

from sys import stderr

from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, SET_NULL
from django.utils.html import SafeString, format_html
from humanize import ordinal

from history.fields import ExtraField, HistoricDateTimeField
from sources.models.source import OldTitledSource
from sources.models.textual_source import OldTextualSource, TextualSource


class Book(TextualSource):
    """A book (as a source)."""

    extra_fields = {
        'translator': 'string',
        'publisher': 'string',
        'edition_number': 'number',
        'edition_year': 'number',
        'printing_number': 'number',
        'volume_number': 'number'
    }

    # translator = jsonstore.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    translator = ExtraField(json_field_name='extra')

    # publisher = jsonstore.CharField(
    #     max_length=100,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    publisher = ExtraField(json_field_name='extra')

    # edition_number = jsonstore.PositiveSmallIntegerField(
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    edition_number = ExtraField(json_field_name='extra')

    # edition_year = jsonstore.CharField(
    #     null=True,
    #     blank=True,
    #     max_length=4,
    #     json_field_name=JSON_FIELD_NAME
    # )

    edition_year = ExtraField(json_field_name='extra')

    # printing_number = jsonstore.PositiveSmallIntegerField(
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    printing_number = ExtraField(json_field_name='extra')

    # volume_number = jsonstore.PositiveSmallIntegerField(
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    volume_number = ExtraField(json_field_name='extra')

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def __html__(self) -> str:
        """Return the book's HTML representation."""
        original_publication_date = (
            self.original_edition.date if self.original_edition else self.original_publication_date
        )
        has_edition_year, has_printing_year = False, False
        if original_publication_date and not self.edition_number:
            has_edition_year = True
        elif original_publication_date and self.printing_number and not self.edition_number:
            has_printing_year = True
        elif self.edition_year and int(self.edition_year) < self.date.year:
            has_printing_year = True

        attributee = self.attributee_string if self.attributee_string else ''
        title_html = f'<i>{self.linked_title}</i>' if self.title else ''

        components = [attributee, title_html]

        # Add edition
        if self.edition_number:
            edition_string = f'{ordinal(self.edition_number)} edition'
            if self.edition_year:
                edition_string = f'{edition_string} ({self.edition_year})'
            components.append(edition_string)
        elif self.edition_year or has_edition_year:
            edition_year = self.edition_year or self.date.year
            edition_string = f'{edition_year} edition'
            if self.original_publication_date:
                edition_string = f'{edition_string} (orig. {self.original_publication_date.year})'
            components.append(edition_string)

        # Add print number
        if self.printing_number and not has_printing_year:
            components.append(f'{ordinal(self.printing_number)} printing')
        elif has_printing_year:
            printing_year_string = f'{self.date.year} printing'
            if self.original_publication_date:
                printing_year_string = f'{printing_year_string} (orig. {self.original_publication_date.year})'
            components.append(printing_year_string)

        components += [
            f'ed. {self.editors}' if self.editors else '',
            f'translated by {self.translator}' if self.translator else '',
            f'{self.publisher}' if self.publisher else '',
            f'vol. {self.volume_number}' if self.volume_number else ''
        ]

        if self.date and not has_edition_year and not has_printing_year:
            components.append(f'{self.date.year}')

        # Remove blank values
        components = [component for component in components if component]

        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')

    def _html(self) -> SafeString:
        """TODO: add docstring."""
        return format_html(self.__html__)
    _html.admin_order_field = 'db_string'
    html = property(_html)


class OldBook(OldTitledSource, OldTextualSource):
    """TODO: add docstring."""

    translator = models.CharField(max_length=100, null=True, blank=True)
    publisher = models.CharField(max_length=100, null=True, blank=True)
    edition_number = models.PositiveSmallIntegerField(null=True, blank=True)
    edition_year = models.CharField(null=True, blank=True, max_length=4)
    printing_number = models.PositiveSmallIntegerField(null=True, blank=True)
    volume_number = models.PositiveSmallIntegerField(null=True, blank=True)
    original_edition = ForeignKey(
        'self',
        related_name='subsequent_editions',
        blank=True,
        null=True,
        on_delete=SET_NULL
    )
    original_publication_date = HistoricDateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        """TODO: write docstring."""
        if self.pk:
            return BeautifulSoup(self.__html__, features='lxml').get_text()
        return ''

    @property
    def __html__(self) -> str:
        """TODO: add docstring."""
        original_publication_date = (
            self.original_edition.date if self.original_edition else self.original_publication_date
        )
        has_edition_year, has_printing_year = False, False
        if original_publication_date and not self.edition_number:
            has_edition_year = True
        elif original_publication_date and self.printing_number and not self.edition_number:
            has_printing_year = True
        elif self.edition_year and int(self.edition_year) < self.date.year:
            has_printing_year = True

        attributee = self.attributee_string if self.attributee_string else ''
        title = f'<i>{self.linked_title}</i>' if self.title else ''

        components = [attributee, title]

        # Add edition
        if self.edition_number:
            edition_string = f'{ordinal(self.edition_number)} edition'
            if self.edition_year:
                edition_string = f'{edition_string} ({self.edition_year})'
            components.append(edition_string)
        elif self.edition_year or has_edition_year:
            edition_year = self.edition_year or self.date.year
            edition_string = f'{edition_year} edition'
            if self.original_publication_date:
                edition_string = f'{edition_string} (orig. {self.original_publication_date.year})'
            components.append(edition_string)

        # Add print number
        if self.printing_number and not has_printing_year:
            components.append(f'{ordinal(self.printing_number)} printing')
        elif has_printing_year:
            printing_year_string = f'{self.date.year} printing'
            if self.original_publication_date:
                printing_year_string = f'{printing_year_string} (orig. {self.original_publication_date.year})'
            components.append(printing_year_string)

        components += [
            f'ed. {self.editors}' if self.editors else '',
            f'translated by {self.translator}' if self.translator else '',
            f'{self.publisher}' if self.publisher else '',
            f'vol. {self.volume_number}' if self.volume_number else ''
        ]

        if self.date and not has_edition_year and not has_printing_year:
            components.append(f'{self.date.year}')

        # Remove blank values
        components = [component for component in components if component]

        # Join components; rearrange commas and double quotes
        return ', '.join(components).replace('",', ',"')

    def _html(self) -> SafeString:
        """TODO: add docstring."""
        return format_html(self.__html__)
    _html.admin_order_field = 'db_string'
    html = property(_html)


class SectionSource(TextualSource):
    """A section (e.g., chapter) of a textual source (e.g., book)."""

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.html, features='lxml').get_text()

    def _html(self) -> SafeString:
        """TODO: add docstring."""
        return format_html(self.__html__)
    _html.admin_order_field = 'db_string'
    html = property(_html)

    def full_clean(self, exclude=None, validate_unique=True):
        """TODO: add docstring."""
        super().full_clean(exclude, validate_unique)
        if self.pk:
            if self.container and not isinstance(self.container, Book):
                raise ValidationError('Chapter container must be a book.')

    @property
    def __html__(self) -> str:
        """Return the section/chapter's HTML representation."""
        container_html = None
        if self.container:
            container_html = self.container.html
            if self.attributee_string:
                if self.attributee_string == self.container.attributee_string:
                    container_html = container_html.replace(f'{self.attributee_string}, ', '')
        if self.attributee_string:
            attributee_string = self.attributee_string
        elif self.container:
            attributee_string = self.container.attributee_string
        else:
            attributee_string = None
        components = [item for item in (attributee_string, f'"{self.linked_title}"') if item]
        if container_html:
            components.append(f'in {container_html}')
        return ', '.join(components).replace('",', ',"')

    @property
    def string(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.html, features='lxml').get_text()


class Section(SectionSource):
    """A section (e.g., of a book or article) as a source."""

    type_label = 'section'


class Chapter(SectionSource):
    """A chapter (of a book) as a source."""

    type_label = 'chapter'


SECTION_TYPES = (
    ('chapter', 'Chapter'),
    ('section', 'Section'),
)


class OldChapter(OldTitledSource, OldTextualSource):
    """TODO: add docstring."""

    type2 = models.CharField(max_length=7, choices=SECTION_TYPES, default='chapter')

    def __str__(self) -> str:
        """TODO: write docstring."""
        return BeautifulSoup(self.__html__, features='lxml').get_text()

    @property
    def html_override(self) -> SafeString:
        """TODO: add docstring."""
        print(f'ALERT: Using html_override for {self}', file=stderr)
        return format_html(self.__html__)

    @property
    def string_override(self) -> SafeString:
        """TODO: add docstring."""
        print(f'ALERT: Using string_override for {self}', file=stderr)
        return format_html(self.html)

    def full_clean(self, exclude=None, validate_unique=True):
        """TODO: add docstring."""
        super().full_clean(exclude, validate_unique)
        if self.pk:
            if self.container and not isinstance(self.container, OldBook):
                raise ValidationError('Chapter container must be a book.')

    @property
    def __html__(self) -> str:
        """TODO: add docstring."""
        container_html = None
        if self.container:
            container_html = self.container.html
            if self.attributee_string:
                if self.attributee_string == self.container.attributee_string:
                    container_html = container_html.replace(f'{self.attributee_string}, ', '')
        if self.attributee_string:
            attributee_string = self.attributee_string
        elif self.container:
            attributee_string = self.container.attributee_string
        else:
            attributee_string = None
        components = [item for item in (attributee_string, f'"{self.linked_title}"') if item]
        if container_html:
            components.append(f'in {container_html}')
        return ', '.join(components).replace('",', ',"')
