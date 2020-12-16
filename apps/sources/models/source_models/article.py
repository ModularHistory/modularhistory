"""Model classes for articles."""

from typing import List, Optional

from django.core.exceptions import ValidationError

from modularhistory.fields import ExtraField

from .piece import SourceWithPageNumbers

JSON_FIELD_NAME = 'extra'


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
