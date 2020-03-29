from typing import Optional

from django.db import models
from django.utils.safestring import SafeText, mark_safe

from .base import TitleMixin, TextualSource

piece_types = (
    ('essay', 'Essay'),
)


class _Piece(TextualSource):
    page_number = models.PositiveSmallIntegerField(null=True, blank=True)
    end_page_number = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def file_page_number(self) -> Optional[int]:
        file = self.get_file()
        if file:
            if self.page_number:
                return self.page_number + file.page_offset
            elif self.container:
                containment = self.source_containments.get(container=self.container)
                if containment.page_number:
                    return containment.page_number + file.page_offset
        return None


class Piece(TitleMixin, _Piece):
    type2 = models.CharField(max_length=10, choices=piece_types, default='essay')

    def __str__(self) -> SafeText:
        string = f'{self.attributee_string}, ' or ''
        string += f'"{self.title_html}"'
        # NOTE: punctuation (quotation marks and commas) are rearranged in the string
        string += f', {self.date.string}' if self.date else ''  # + (', ' if self.container else '')
        string = string.replace('",', ',"')
        return mark_safe(string)
