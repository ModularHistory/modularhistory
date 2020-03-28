from django.db import models
from django.utils.safestring import SafeText, mark_safe

from .base import TitleMixin, _Piece

piece_types = (
    ('essay', 'Essay'),
)


class Piece(TitleMixin, _Piece):
    type2 = models.CharField(max_length=10, choices=piece_types, default='essay')

    def __str__(self) -> SafeText:
        string = f'{self.attributee_string}, ' or ''
        string += f'"{self.title}"'
        # NOTE: punctuation (quotation marks and commas) are rearranged in the string
        string += f', {self.date.string}' if self.date else ''  # + (', ' if self.container else '')
        string = string.replace('",', ',"')
        return mark_safe(string)
