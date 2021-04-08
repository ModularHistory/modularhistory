from typing import Optional

from django.db.models import SET_NULL, ForeignKey
from pydantic import BaseModel, Field

from apps.sources.models.source import Source
from modularhistory.fields import ExtraField, HistoricDateTimeField

JSON_FIELD_NAME = 'extra'

STRING = 'string'
NUMBER = 'number'


class TextualSource(Source):
    """Mixin model for textual sources."""

    original_edition = ForeignKey(
        to='self',
        related_name='subsequent_editions',
        blank=True,
        null=True,
        on_delete=SET_NULL,
    )
    original_publication_date = HistoricDateTimeField(null=True, blank=True)

    editors = ExtraField(json_field_name=JSON_FIELD_NAME, null=True, blank=True)

    class ExtraFieldSchema(BaseModel):
        editors: str = Field(default=None)

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
