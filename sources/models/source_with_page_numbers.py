from typing import Optional

from modularhistory.fields import ExtraField
from sources.models.textual_source import TextualSource

TYPE_MAX_LENGTH: int = 10

JSON_FIELD_NAME = 'extra'


class SourceWithPageNumbers(TextualSource):
    """Mixin model for sources with page numbers."""

    page_number = ExtraField(
        json_field_name=JSON_FIELD_NAME,
        null=True,
        blank=True,
    )
    end_page_number = ExtraField(
        json_field_name=JSON_FIELD_NAME,
        null=True,
        blank=True,
    )

    extra_fields = {
        'page_number': 'number',
        'end_page_number': 'number',
        **TextualSource.extra_fields,
    }

    @property
    def file_page_number(self) -> Optional[int]:
        """Return the page number to use for opening the source's associated file."""
        file = self.source_file
        if file and self.page_number:
            return self.page_number + file.page_offset
        elif self.containment and self.containment.page_number:
            return self.containment.page_number + file.page_offset
        return None
