from typing import Optional

from django.db.models import BooleanField
from django.utils.safestring import SafeText, mark_safe

from history.fields import HistoricDateTimeField
from .base_model import Model


class DatedModel(Model):
    date_is_circa = BooleanField(blank=True, default=False)
    date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def _date_string(self) -> str:
        date_string = self.date.string if self.date else ''
        if date_string and self.date_is_circa and not date_string.startswith('c. '):
            date_string = f'c. {date_string}'
        if hasattr(self, 'end_date') and self.end_date:
            date_string = f'{date_string} – {self.end_date.string}'
        return date_string
    _date_string.admin_order_field = 'date'
    date_string = property(_date_string)

    @property
    def date_html(self) -> Optional[SafeText]:
        if not self.date:
            return None
        date_html = self.date.html
        if date_html and self.date_is_circa and not date_html.startswith('c. '):
            date_html = f'c. {date_html}'
        if hasattr(self, 'end_date') and self.end_date:
            date_html = f'{date_html} – {self.end_date.html}'
        if self.date.year < 1000 and not self.date.is_bce and not date_html.endswith(' CE'):
            date_html += ' CE'
        return mark_safe(date_html)
