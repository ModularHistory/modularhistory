"""Model classes for articles."""

from typing import List, Optional

from django.core.exceptions import ValidationError
from django.db import models

from apps.sources.models import PolymorphicSource
from apps.sources.models.sources.source_with_page_numbers import PageNumbersMixin
from modularhistory.fields import ExtraField

from .piece import SourceWithPageNumbers

JSON_FIELD_NAME = 'extra'


class PolymorphicArticle(PolymorphicSource, PageNumbersMixin):
    """An article published by a journal, magazine, or newspaper."""

    publication = models.ForeignKey(to='sources.Publication', on_delete=models.PROTECT)
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    volume = models.PositiveSmallIntegerField(null=True, blank=True)

    def clean(self):
        """Prepare the article to be saved."""
        super().clean()
        if not self.publication:
            raise ValidationError('Article must have an associated publication.')

    def __html__(self) -> str:
        """Return the article's citation HTML string."""
        title = self.linked_title.replace('"', "'") if self.linked_title else ''
        components: List[Optional[str]] = [
            self.attributee_html,
            f'"{title}"' if title else '',
            self.publication.html,
            f'vol. {self.volume}' if self.volume else '',
            f'no. {self.number}' if self.number else '',
            self.date.string if self.date else '',
        ]
        return self.components_to_html(components)


class Article(SourceWithPageNumbers):
    """A published article (as a source)."""

    number = ExtraField(json_field_name=JSON_FIELD_NAME, null=True, blank=True)
    volume = ExtraField(json_field_name=JSON_FIELD_NAME, null=True, blank=True)

    class FieldNames(SourceWithPageNumbers.FieldNames):
        number = 'number'
        volume = 'volume'

    extra_field_schema = {
        FieldNames.volume: 'number',
        FieldNames.number: 'number',
        **SourceWithPageNumbers.extra_field_schema,
    }
    inapplicable_fields = [
        FieldNames.collection,
    ]
    searchable_fields = [FieldNames.string, 'publication__name']

    def clean(self):
        """Prepare the article to be saved."""
        super().clean()
        if not self.publication:
            raise ValidationError('Article must have an associated publication.')

    def __html__(self) -> str:
        """
        Return the article's HTML string representation.

        The string has the following form:
            ... TODO
        """
        attributee_html = self.attributee_html
        title = self.linked_title.replace('"', "'") if self.linked_title else ''
        publication_html = (
            self.publication.html if self.publication else ''
        )  # TODO: make required
        volume = f'vol. {self.volume}' if self.volume else ''
        number = f'no. {self.number}' if self.number else ''
        date = self.date.string if self.date else ''
        components: List[Optional[str]] = [
            attributee_html,
            f'"{title}"' if title else '',
            publication_html,
            volume,
            number,
            date,
        ]
        return self.components_to_html(components)
