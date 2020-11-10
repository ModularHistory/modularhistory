from typing import Optional

from django.db.models import BooleanField
from django.utils.html import format_html
from django.utils.safestring import SafeString

from modularhistory.fields import HistoricDateTimeField
from modularhistory.models.model import Model
from modularhistory.models.model_with_computations import retrieve_or_compute
from modularhistory.structures import HistoricDateTime
from modularhistory.utils.html import soupify

CIRCA_PREFIX = 'c. '


class DatedModel(Model):
    """A model with a date (e.g., a quote or occurrence)."""

    date_is_circa = BooleanField(blank=True, default=False)
    date = HistoricDateTimeField(null=True, blank=True)

    class Meta:
        """
        Meta options for DatedModel.

        See https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options.
        """

        abstract = True

    def date_string(self) -> str:
        """Return the string representation of the model instance's date."""
        date_html = self.date_html
        return soupify(date_html).get_text() if date_html else ''

    date_string.admin_order_field = 'date'
    date_string = property(date_string)  # type: ignore

    @property  # type: ignore
    @retrieve_or_compute(caster=format_html)
    def date_html(self) -> SafeString:
        """Return the HTML representation of the model instance's date."""
        date, date_html = self.get_date(), ''
        if date:
            date_html = f'{date.html}'
            date_html_requires_circa_prefix = (
                date_html
                and self.date_is_circa
                and not date_html.startswith(CIRCA_PREFIX)
            )
            if date_html_requires_circa_prefix:
                date_html = f'{CIRCA_PREFIX}{date_html}'
            if getattr(self, 'end_date', None):
                date_html = f'{date_html} – {self.end_date.html}'
            use_ce = (
                self.date.year < 1000
                and not self.date.is_bce
                and not date_html.endswith(' CE')
            )
            if use_ce:
                date_html = f'{date_html} CE'
        return format_html(date_html)

    @property
    def year_html(self) -> Optional[SafeString]:
        """Return the HTML representation of the model instance's date's year."""
        if not self.date:
            return None
        year_html = self.date.year_string
        if self.date_is_circa and not self.date.month_is_known:
            year_html = f'{CIRCA_PREFIX}{year_html}'
            year_html = year_html.replace(f'{CIRCA_PREFIX}{CIRCA_PREFIX}', CIRCA_PREFIX)
        return format_html(year_html)

    def get_date(self) -> Optional[HistoricDateTime]:
        """
        Determine and return the model instance's date.

        Override this to retrieve date values through other means,
        e.g., by inspecting related objects.
        """
        return self.date or None
