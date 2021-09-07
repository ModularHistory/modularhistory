"""Widget for HistoricDateTime."""

import re
from datetime import date, datetime
from typing import Any, Optional, Union

from django import forms
from django.forms import MultiWidget
from sigfig import round

from apps.dates.structures import (
    BP_REFERENCE_YEAR,
    DECIMAL_INVERSION_BASIS,
    EXPONENT_INVERSION_BASIS,
    SEASONS,
    HistoricDateTime,
    get_month_from_season,
    get_season_from_month,
)
from core.constants.strings import COLON, PERIOD, SPACE

CE = 'CE'
BCE = 'BCE'
YBP = 'YBP'

year_systems = ((CE, 'CE'), (BCE, 'BCE'), (YBP, 'YBP'))


def get_year(year: int, year_system: str = CE) -> tuple[int, int, int]:
    """
    Return a decompressed year value (year, second, microsecond) ready for storage.

    For years before common era,
    - the year value is set to 1, and
    - second and microsecond values are set.
    The second and microsecond values are used to:
    - correctly sort datetimes in the db and
    - determine the actual year upon retrieval from the db.
    """
    year = int(year)
    if year > HistoricDateTime.bce_threshold and year_system != YBP:
        # Safe to assume this should be YBP
        year_system = YBP
    microsecond, second = 0, 0
    if year_system not in {CE, BCE, YBP}:
        raise ValueError
    elif year_system in {BCE, YBP}:
        year = year if year_system == BCE else year - BP_REFERENCE_YEAR
        year = round(year, sigfigs=HistoricDateTime.significant_figures)
        # Build a year stamp with max 6 digits, e.g., '1.3800e+10' for the Big Bang.
        scientific_notation: str = '{:.4e}'.format(year)  # noqa: P101
        decimal_num_str, exponent_str = scientific_notation.split('e+')
        exponent = int(exponent_str)
        decimal_num = int(decimal_num_str.replace(PERIOD, ''))  # 10, 13800 for the Big Bang
        inv_exponent = EXPONENT_INVERSION_BASIS - exponent
        inv_decimal_num = DECIMAL_INVERSION_BASIS - int(decimal_num)
        second, microsecond = inv_exponent, inv_decimal_num
        year = 1
    return year, second, microsecond


class YearInput(MultiWidget):
    """Widget for inputting year values."""

    template_name = 'forms/year_input.html'

    def __init__(self, attrs: Optional[dict] = None):
        """Construct the year input widget."""
        attrs = attrs or {'class': 'form-control'}
        widgets = [
            forms.NumberInput(attrs={**attrs, **{'min': '1', 'class': 'form-control'}}),
            forms.Select(attrs=attrs, choices=year_systems),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, datetime_value: Union[HistoricDateTime, int, str]):
        """Decompress a datetime value into year and year_system values."""
        year, year_system = (None, None)
        if isinstance(datetime_value, HistoricDateTime):
            if datetime_value.use_ybp:
                year, year_system = datetime_value.year_bp, YBP
            elif datetime_value.is_bce:
                year, year_system = datetime_value.year_bce, BCE
            else:
                year_system = CE
        elif datetime_value:
            return [datetime_value, CE]
        return [year, year_system]

    def value_from_datadict(self, datadict, files, name) -> Optional[str]:
        """Compress the input value into a format that can be saved to the db."""
        decompressed_values = super().value_from_datadict(datadict, files, name)
        if len(decompressed_values) != 2:
            raise ValueError(f'Wrong number of values: {len(decompressed_values)}')
        year, year_system = decompressed_values
        if not year:
            return None
        year, second, microsecond = get_year(year, year_system)
        # Build datetime obj
        dt = HistoricDateTime(year, 1, 1, 1, 1, second, microsecond=microsecond)
        # Return date-parsable string for db
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


class HistoricDateWidget(MultiWidget):
    """Widget for dates that may be before common era and have variable specificity."""

    def __init__(self, attrs: Optional[dict] = None):
        """Construct the widget."""
        default_attrs = {'style': 'margin-right: 0.5rem; min-width: 4rem;'}
        attrs = {**attrs, **default_attrs} if attrs else default_attrs
        placeholder_key, min_key, max_key = 'placeholder', 'min', 'max'
        today = date.today()
        widgets = [
            forms.NumberInput(
                attrs={**attrs, **{placeholder_key: 'Year', min_key: 1, max_key: today.year}}
            ),
            forms.Select(attrs=attrs, choices=year_systems),
            forms.Select(attrs=attrs, choices=SEASONS),
            forms.NumberInput(
                attrs={**attrs, **{placeholder_key: 'Month', min_key: 1, max_key: 12}}
            ),
            forms.NumberInput(
                attrs={**attrs, **{placeholder_key: 'Day', min_key: 1, max_key: 31}}
            ),
            forms.HiddenInput(attrs={**attrs}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, datetime_value: Union[date, str, Any]):
        """
        "Decompresses" a Python value into a list of values to populate the widget.

        The input value can be assumed valid, but not necessarily non-empty.

        https://docs.djangoproject.com/en/dev/ref/forms/widgets/#django.forms.MultiWidget.decompress
        """
        nones = (None, None, None, None, None, None)
        hour = minute = second = ms = 0
        if not isinstance(datetime_value, HistoricDateTime):
            if isinstance(datetime_value, str):
                year, month, day, hour, minute, second, ms = self._parse_string(
                    datetime_value
                )
            elif isinstance(datetime_value, (datetime, date)):
                year, month, day = (
                    datetime_value.year,
                    datetime_value.month,
                    datetime_value.day,
                )
                if isinstance(datetime_value, datetime):
                    hour, minute, second, ms = (
                        datetime_value.hour,
                        datetime_value.minute,
                        datetime_value.second,
                        datetime_value.microsecond,
                    )
            else:
                return nones
            # Convert value to HistoricDateTime
            datetime_value = HistoricDateTime(year, month, day, hour, minute, second, ms)
        return self._decompress_historic_datetime(datetime_value)

    def value_from_datadict(self, datadict, files, name) -> Optional[str]:
        """Compress the input value into a format that can be saved to the db."""
        full_n_values, min_n_values = 6, 3
        decompressed_values = [
            _ or 0 for _ in super().value_from_datadict(datadict, files, name)
        ]
        n_values = len(decompressed_values)
        if n_values < min_n_values:
            raise ValueError(f'Wrong number of values: {len(decompressed_values)}')
        elif n_values < full_n_values:
            decompressed_values.extend(None for _ in range(full_n_values - n_values))
        year, year_system, season, month, day, time = decompressed_values
        if not year:
            return None
        dt = _datetime_from_datadict_values(year, year_system, season, month, day)
        # Get date-parsable string for db
        dt_string = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        # Ensure the year is 4 digits; add leading zeros if necessary
        incomplete_year_pattern = re.compile(r'^(\d{1,3})(-.+)')
        incomplete_year_match = incomplete_year_pattern.match(dt_string)
        if incomplete_year_match:
            year_string = incomplete_year_match.group(1)
            year_string = f'{year_string:0>4}'
            dt_string = incomplete_year_pattern.sub(rf'{year_string}\g<2>', dt_string)
        return dt_string

    @staticmethod
    def _decompress_historic_datetime(historic_datetime: HistoricDateTime) -> list:
        year = historic_datetime.year
        season, month, day, time = None, None, None, None
        hour, minute, second = (
            historic_datetime.hour,
            historic_datetime.minute,
            historic_datetime.second,
        )
        if historic_datetime.use_ybp:
            year, year_system = historic_datetime.year_bp, YBP
        elif historic_datetime.year_bce:
            year, year_system = historic_datetime.year_bce, BCE
        else:
            year_system = CE
        if historic_datetime.season_is_known:
            season = get_season_from_month(historic_datetime.month)
            if historic_datetime.month_is_known:
                month = historic_datetime.month
                if historic_datetime.day_is_known:
                    day = historic_datetime.day
        if 0 in {hour, minute, second} or 1 in {hour, minute, second}:
            time = None
        else:
            time = historic_datetime.strftime('%H:%M:%S.%f')
        return [year, year_system, season, month, day, time]

    def _parse_string(self, datetime_string: str) -> tuple[int, ...]:
        """TODO: move elsewhere, perhaps."""
        year, month, day = datetime_string.split('-')
        hour = minute = second = microsecond = '0'
        if SPACE in day:
            day, time = day.split(SPACE)
            if COLON in time:
                hour, minute, second = time.split(COLON)
                if PERIOD in second:
                    second, microsecond = second.split(PERIOD)
        str_values = (year, month, day, hour, minute, second, microsecond)
        return tuple(int(string) for string in str_values)


def _datetime_from_datadict_values(
    year: int, year_system, season=None, month=None, day=None
) -> HistoricDateTime:
    # Figure out year
    year, second, microsecond = get_year(year, year_system)
    # Figure out date precision
    hour, minute = 0, 0
    if not season and not month:
        hour, minute, second = 1, 1, second or 1
    elif season and not month:
        month = get_month_from_season(season)
        hour, minute, second = 0, 1, second or 1
    elif month and not day:
        hour, minute, second = 0, 0, second or 1
    month, day = (month or 1), (day or 1)
    # Return datetime object
    return HistoricDateTime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
        microsecond=int(microsecond),
    )
