import logging
from typing import Optional

from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.utils.translation import ugettext_lazy as _

from apps.dates.fields import HistoricDateTimeField
from apps.dates.structures import HistoricDateTime
from core.models.model import ExtendedModel

CIRCA_PREFIX = 'c. '


class DatedModel(ExtendedModel):
    """A model with a date (e.g., a quote or occurrence)."""

    # `date_nullable` can be set to True by child models that require the
    # date field to be nullable for any reason.
    date_nullable: bool = False

    date = HistoricDateTimeField(
        verbose_name=_('date'),
        # `date` must be nullable at the db level (because some inheriting models
        # might require such), but if no date is set, we use the `clean` method
        # to raise a ValidationError unless the child model whitelists itself
        # by setting `date_nullable` to True.
        null=True,
        blank=True,
    )
    end_date = HistoricDateTimeField(
        verbose_name=_('end date'),
        null=True,
        blank=True,
    )
    date_is_circa = models.BooleanField(
        verbose_name=_('date is circa'),
        blank=True,
        default=False,
        help_text='whether the date is estimated/imprecise',
    )

    date_string = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        editable=False,
        verbose_name=_('date string'),
    )
    date_string.admin_order_field = 'date'  # type: ignore

    # https://docs.djangoproject.com/en/dev/ref/models/options/#model-meta-options
    class Meta:
        abstract = True

    def clean(self, *args, **kwargs):
        if isinstance(self.date, str):
            self.date = HistoricDateTime.from_iso(self.date)
        if isinstance(self.end_date, str):
            self.end_date = HistoricDateTime.from_iso(self.end_date)
        self.date_string = self.get_date_string()
        super().clean()

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

    def get_date_string(self) -> str:
        """Return the string representation of the model instance's date."""
        date, date_string = self.get_date(), ''
        if date:
            date_string = (
                f'{date.string}' if isinstance(date, HistoricDateTime) else f'{date}'
            )
            date_string_requires_circa_prefix = (
                date_string and self.date_is_circa and CIRCA_PREFIX not in date_string
            )
            if date_string_requires_circa_prefix:
                date_string = f'{CIRCA_PREFIX}{date_string}'
            end_date: Optional[HistoricDateTime] = getattr(self, 'end_date', None)
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

    def get_date(self) -> Optional[HistoricDateTime]:
        """
        Determine and return the model instance's date.

        Override this to retrieve date values through other means,
        e.g., by inspecting related objects.
        """
        if self.date:
            if not isinstance(self.date, HistoricDateTime):
                logging.error(
                    f'`date` attribute of {self.__class__.__name__} '
                    f'has non-HistoricDateTime value of {self.date}'
                )
            return self.date
        return None
