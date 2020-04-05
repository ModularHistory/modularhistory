from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, SET_NULL
from django.utils.safestring import SafeText, mark_safe
from humanize import ordinal

from history.fields import HistoricDateTimeField
from .base import TitleMixin, TextualSource


class _Book(TitleMixin, TextualSource):
    translator = models.CharField(max_length=100, null=True, blank=True)
    publisher = models.CharField(max_length=100, null=True, blank=True)
    edition_number = models.PositiveSmallIntegerField(null=True, blank=True)
    edition_year = models.CharField(null=True, blank=True, max_length=4)
    printing_number = models.PositiveSmallIntegerField(null=True, blank=True)
    volume_number = models.PositiveSmallIntegerField(null=True, blank=True)
    original_book = ForeignKey(
        'self', related_name='subsequent_editions',
        blank=True, null=True,
        on_delete=SET_NULL
    )
    original_publication_date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def _html(self) -> str:
        raise NotImplementedError


section_types = (
    ('chapter', 'Chapter'),
    ('section', 'Section'),
)


class Chapter(TitleMixin, TextualSource):
    type2 = models.CharField(max_length=7, choices=section_types, default='chapter')

    def __str__(self):
        return BeautifulSoup(self._html, features='lxml').get_text()

    @property
    def book(self) -> 'Book':
        return self.container

    @property
    def book_title(self):
        return self.book.title

    @property
    def _html(self) -> str:
        if not self.book:
            return ''
        book_html = self.book.html
        if all([self.attributee_string, self.book, self.book.attributee_string,
                self.attributee_string == self.book.attributee_string]):
            book_html = book_html.replace(f'{self.attributee_string}, ', '')
        attributee_string = self.attributee_string or self.book.attributee_string
        html = f'{attributee_string}, "{self.title_html}," in {book_html}'
        return html

    @property
    def html_override(self) -> SafeText:
        return mark_safe(self._html)

    @property
    def string_override(self) -> SafeText:
        return mark_safe(self.html)

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude, validate_unique)
        if self.container and not isinstance(self.container, Book):
            raise ValidationError('Chapter container must be a book.')


class Book(_Book):
    def __str__(self):
        return BeautifulSoup(self._html, features='lxml').get_text()

    @property
    def _html(self) -> str:
        string = f'{self.attributee_string}, ' if self.attributee_string else ''
        string += f'<i>{self.title_html}</i>'
        original_publication_date = (self.original_book.date if self.original_book
                                     else self.original_publication_date)
        has_edition_year, has_printing_year = False, False
        if original_publication_date and not self.edition_number:
            has_edition_year = True
        elif original_publication_date and self.printing_number and not self.edition_number:
            has_printing_year = True
        elif self.edition_year and int(self.edition_year) < self.date.year:
            has_printing_year = True
        if self.edition_number:
            string += f', {ordinal(self.edition_number)} edition'
            if self.edition_year:
                string += f' ({self.edition_year})'
        elif self.edition_year or has_edition_year:
            edition_year = self.edition_year or self.date.year
            string += f', {edition_year} edition'
            string += (f' (orig. {self.original_publication_date.year})'
                       if self.original_publication_date else '')
        if self.printing_number and not has_printing_year:
            string += f', {ordinal(self.printing_number)} printing'
        elif has_printing_year:
            string += f', {self.date.year} printing'
            string += (f' (orig. {self.original_publication_date.year})'
                       if self.original_publication_date else '')
        string += f', ed. {self.editors}' if self.editors else ''
        string += f', translated by {self.translator}' if self.translator else ''
        string += f', {self.publisher}' if self.publisher else ''
        string += f', vol. {self.volume_number}' if self.volume_number else ''
        if not has_edition_year and not has_printing_year:
            string += f', {self.date.year}' if self.date else ''
        return string

    def html(self) -> SafeText:
        return mark_safe(self._html)
    html.admin_order_field = 'db_string'
    html = property(html)
