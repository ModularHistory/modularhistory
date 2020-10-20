from typing import Optional

from django.db.models import ForeignKey, SET_NULL

from modularhistory.fields import ExtraField, HistoricDateTimeField
from sources.models.source import Source

JSON_FIELD_NAME = 'extra'


class TextualSource(Source):
    """Mixin model for textual sources."""

    original_edition = ForeignKey(
        'self',
        related_name='subsequent_editions',
        blank=True,
        null=True,
        on_delete=SET_NULL
    )
    original_publication_date = HistoricDateTimeField(null=True, blank=True)

    # editors = jsonstore.CharField(
    #     max_length=MAX_CREATOR_STRING_LENGTH,
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    editors = ExtraField(json_field_name=JSON_FIELD_NAME)

    @property
    def file_page_number(self) -> Optional[int]:
        """TODO: write docstring."""
        file = self.source_file
        if file:
            if self.containment and self.containment.page_number:
                return self.containment.page_number + file.page_offset
            return file.first_page_number + file.page_offset
        return None

    @property
    def source_file_url(self) -> Optional[str]:
        """TODO: write docstring."""
        file_url = super().source_file_url
        if file_url and self.file_page_number:
            file_url = f'{file_url}#page={self.file_page_number}'
        return file_url
