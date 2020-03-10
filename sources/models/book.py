from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ForeignKey, SET_NULL
from django.utils.safestring import SafeText, mark_safe

from history.fields import HistoricDateField
from .base import TitleMixin, TextualSource


class _Book(TitleMixin, TextualSource):
    translator = models.CharField(max_length=100, null=True, blank=True)
    publisher = models.CharField(max_length=100, null=True, blank=True)
    edition_number = models.PositiveSmallIntegerField(default=1)
    volume_number = models.PositiveSmallIntegerField(null=True, blank=True)
    original_book = ForeignKey('self', related_name='subsequent_editions', blank=True, null=True, on_delete=SET_NULL)
    original_publication_date = HistoricDateField(null=True, blank=True)

    class Meta:
        abstract = True


section_types = (
    ('chapter', 'Chapter'),
    ('section', 'Section'),
)


class Chapter(TitleMixin, TextualSource):
    type2 = models.CharField(max_length=7, choices=section_types, default='chapter')

    def __str__(self):
        book_str = str(self.book)
        if all([self.creator_string, self.book, self.book.creator_string,
                self.creator_string == self.book.creator_string]):
            book_str = book_str.replace(f'{self.creator_string}, ', '')
        return f'{self.creator_string or self.book.creator_string}, "{self.title}," in {book_str}'

    @property
    def book(self) -> 'Book':
        return self.container

    @property
    def book_title(self):
        return self.book.title

    @property
    def html(self) -> SafeText:
        html = str(self)
        return mark_safe(html)

    @property
    def string_override(self) -> SafeText:
        return mark_safe(self.html)

    def full_clean(self, exclude=None, validate_unique=True):
        super().full_clean(exclude, validate_unique)
        if self.container and not isinstance(self.container, Book):
            raise ValidationError('Chapter container must be a book.')

class Book(_Book):
    def __str__(self):
        return self.html

    @property
    def html(self) -> SafeText:
        string = f'{self.creator_string}, ' if self.creator_string else ''
        string += f'<i>{self.title}</i>'
        has_edition_year = ((self.edition_number and self.edition_number > 1)
                            or self.original_book or self.original_publication_date)
        if has_edition_year:
            string += f', {self.date.year} edition'
            string += f' (orig. {self.original_publication_date.year})' if self.original_publication_date else ''
        string += f', ed. {self.editors}' if self.editors else ''
        string += f', translated by {self.translator}' if self.translator else ''
        string += f', {self.publisher}' if self.publisher else ''
        string += f', vol. {self.volume_number}' if self.volume_number else ''
        if not has_edition_year:
            string += f', {self.date.year}' if self.date else ''
        return mark_safe(string)
