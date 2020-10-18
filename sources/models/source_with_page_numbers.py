from typing import Optional

from modularhistory.fields import ExtraField
from sources.models.textual_source import TextualSource

TYPE_MAX_LENGTH: int = 10


class SourceWithPageNumbers(TextualSource):
    """Mixin model for sources with page numbers."""

    # page_number = jsonstore.fields.PositiveSmallIntegerField(
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    page_number = ExtraField(json_field_name='extra')

    # end_page_number = jsonstore.fields.PositiveSmallIntegerField(
    #     null=True,
    #     blank=True,
    #     json_field_name=JSON_FIELD_NAME
    # )

    end_page_number = ExtraField(json_field_name='extra')

    @property
    def file_page_number(self) -> Optional[int]:
        """Returns the page number to use for opening the source's associated file."""
        file = self.file
        if file:
            if self.page_number:
                return self.page_number + file.page_offset
            elif self.container:
                containment = self.source_containments.get(container=self.container)
                if containment.page_number:
                    return containment.page_number + file.page_offset
        return None
