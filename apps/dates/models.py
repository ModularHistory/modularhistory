from typing import Optional

from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.dates.fields import HistoricDateTimeField
from core.models.model import Model
from core.models.model_with_computations import retrieve_or_compute
from core.structures import HistoricDateTime
from core.utils.html import soupify

CIRCA_PREFIX = 'c. '


class DatedModel(Model):
    """A model with a date (e.g., a quote or occurrence)."""

    date_is_circa = models.BooleanField(
        verbose_name=_('date is circa'),
        blank=True,
        default=False,
        help_text='whether the date is estimated/imprecise',
    )
    date = HistoricDateTimeField(verbose_name=_('date'), null=True)

    class Meta:
        """Meta options for DatedModel."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True

    def date_string(self) -> str:
        """Return the string representation of the model instance's date."""
        date_html = self.date_html
        return soupify(date_html).get_text() if date_html else ''

    date_string.admin_order_field = 'date'  # type: ignore
    date_string = property(date_string)  # type: ignore

    @property  # type: ignore
    @retrieve_or_compute(caster=format_html)
    def date_html(self) -> SafeString:
        """Return the HTML representation of the model instance's date."""
        date, date_html = self.get_date(), ''
        if date:
            date_html = f'{date.html}'
            date_html_requires_circa_prefix = (
                date_html and self.date_is_circa and CIRCA_PREFIX not in date_html
            )
            if date_html_requires_circa_prefix:
                date_html = f'{CIRCA_PREFIX}{date_html}'
            end_date = getattr(self, 'end_date', None)
            if end_date:
                date_html = f'{date_html} – {end_date.html}'
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
