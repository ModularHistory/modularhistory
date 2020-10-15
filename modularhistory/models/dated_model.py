from typing import Optional

from django.db.models import BooleanField
from django.utils.safestring import SafeString
from django.utils.html import format_html

from modularhistory.fields import HistoricDateTimeField
from modularhistory.models import Model
from modularhistory.structures import HistoricDateTime


class DatedModel(Model):
    """A model with a date (e.g., a quote or occurrence)."""

    date_is_circa = BooleanField(blank=True, default=False)
    date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def _date_string(self) -> str:
        """TODO: add docstring."""
        date_string = self.date.string if self.date else ''
        if date_string and self.date_is_circa and not date_string.startswith('c. '):
            date_string = f'c. {date_string}'
        if hasattr(self, 'end_date') and self.end_date:
            date_string = f'{date_string} – {self.end_date.string}'
        return date_string
    _date_string.admin_order_field = 'date'
    date_string = property(_date_string)

    @property
    def date_html(self) -> Optional[SafeString]:
        """TODO: add docstring."""
        date = self.get_date()
        if not date:
            return None
        date_html = f'{date.html}'
        if date_html and self.date_is_circa and not date_html.startswith('c. '):
            date_html = f'c. {date_html}'
            date_html = date_html.replace('c. c. ', 'c. ')
        if hasattr(self, 'end_date') and self.end_date:
            date_html = f'{date_html} – {self.end_date.html}'
        if self.date.year < 1000 and not self.date.is_bce and not date_html.endswith(' CE'):
            date_html = f'{date_html} CE'
        return format_html(date_html)

    @property
    def year_html(self) -> Optional[SafeString]:
        """TODO: add docstring."""
        if not self.date:
            return None
        year_html = self.date.year_string
        if self.date_is_circa and not self.date.month_is_known:
            year_html = f'c. {year_html}'
            year_html = year_html.replace('c. c. ', 'c. ')
        return format_html(year_html)

    def get_date(self) -> Optional[HistoricDateTime]:
        """
        Determine and return the obj's date.

        Override this to retrieve date values through other means,
        e.g., by inspecting related objects.
        """
        return self.date or None
