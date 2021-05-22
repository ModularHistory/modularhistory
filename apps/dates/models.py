from typing import Optional

from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.dates.fields import HistoricDateTimeField
from apps.dates.structures import HistoricDateTime
from core.models.model import Model
from core.models.model_with_cache import store

CIRCA_PREFIX = 'c. '


class DatedModel(Model):
    """A model with a date (e.g., a quote or occurrence)."""

    date_is_circa = models.BooleanField(
        verbose_name=_('date is circa'),
        blank=True,
        default=False,
        help_text='whether the date is estimated/imprecise',
    )
    date = HistoricDateTimeField(
        verbose_name=_('date'),
        null=True,
        # Defer to the `clean` method for determining whether to require a date.
        blank=True,
    )
    end_date = HistoricDateTimeField(
        verbose_name=_('end date'),
        null=True,
        blank=True,
    )

    class Meta:
        """Meta options for DatedModel."""

        # https://docs.djangoproject.com/en/3.1/ref/models/options/#model-meta-options

        abstract = True

    @store
    def date_string(self) -> str:
        """Return the string representation of the model instance's date."""
        date, date_string = self.get_date(), ''
        if date:
            date_string = f'{date.string}'
            date_string_requires_circa_prefix = (
                date_string and self.date_is_circa and CIRCA_PREFIX not in date_string
            )
            if date_string_requires_circa_prefix:
                date_string = f'{CIRCA_PREFIX}{date_string}'
            end_date = getattr(self, 'end_date', None)
            if end_date:
                date_string = f'{date_string} – {end_date.string}'
            use_ce = (
                self.date.year < 1000
                and not self.date.is_bce
                and not date_string.endswith(' CE')
            )
            if use_ce:
                date_string = f'{date_string} CE'
        return date_string

    date_string.admin_order_field = 'date'  # type: ignore
    date_string = property(date_string)  # type: ignore

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
