"""Widget for HistoricDateTime."""

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from django import forms
from django.forms import MultiWidget
from sigfig import round

from modularhistory.structures.historic_datetime import (
    HistoricDateTime,
    SEASONS,
    get_month_from_season,
    get_season_from_month
)

CE = 'CE'
BCE = 'BCE'
YBP = 'YBP'

year_systems = (
    (CE, 'CE'),
    (BCE, 'BCE'),
    (YBP, 'YBP')
)

YBP_BASIS = 1950  # YBP is generally calculated based on the year 1950
SIGNIFICANT_FIGURES = 4


def get_year(year: int, year_system: str = CE) -> Tuple[int, int, int]:
    """TODO: add docstring."""
    year = int(year)
    if year > HistoricDateTime.bce_threshold and year_system != YBP:
        # Safe to assume this should be YBP
        print(f'Using YBP year system instead of {year_system} ...')
        year_system = YBP
    microsecond, second = 0, 0
    if year_system not in {CE, BCE, YBP}:
        raise ValueError
    elif year_system in {BCE, YBP}:
        exponent_inversion_basis = 30  # --> 20 for the Big Bang
        decimal_inversion_basis = 100000  # --> 986200 for the Big Bang
        year = year if year_system == BCE else year - YBP_BASIS
        year = round(year, sigfigs=HistoricDateTime.significant_figures)
        # Build a year stamp with max 6 digits
        scientific_notation: str = '{:.4e}'.format(year)  # '1.3800e+10' for the Big Bang
        decimal_num_str, exponent_str = scientific_notation.split('e+')
        exponent, decimal_num = int(exponent_str), int(decimal_num_str.replace('.', ''))  # 10, 13800 for the Big Bang
        inv_exponent = exponent_inversion_basis - exponent
        inv_decimal_num = decimal_inversion_basis - int(decimal_num)
        second, microsecond = inv_exponent, inv_decimal_num
        year = 1
        # TODO
        # if year_system == BCE:
        #     pass
        # elif year_system == YBP:
        #     pass
    return year, second, microsecond


class YearInput(MultiWidget):
    """TODO: add docstring."""

    template_name = 'forms/year_input.html'

    def __init__(self, attrs: Optional[Dict] = None):
        """TODO: add docstring."""
        attrs = attrs or {'class': 'form-control'}
        widgets = [
            forms.NumberInput(attrs={**attrs, **{'min': '1', 'class': 'form-control'}}),
            forms.Select(attrs=attrs, choices=year_systems),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Union[HistoricDateTime, int, str]):
        """TODO: add docstring."""
        year, year_system = (None, None)
        if isinstance(value, HistoricDateTime):
            if value.use_ybp:
                year, year_system = value.year_bp, YBP
            elif value.is_bce:
                year, year_system = value.year_bce, BCE
            else:
                year_system = CE
        elif value:
            return [value, CE]
        return [year, year_system]

    def value_from_datadict(self, data, files, name) -> Optional[str]:
        """TODO: write docstring."""
        values = super().value_from_datadict(data, files, name)
        if len(values) != 2:
            raise ValueError(f'Wrong number of values to unpack: {len(values)}')
        year, year_system = values
        if not year:
            return None
        year, second, microsecond = get_year(year, year_system)
        # Build datetime obj
        dt = HistoricDateTime(year, 1, 1, 1, 1, second, microsecond=microsecond)
        # Return date-parsable string for db
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


class HistoricDateWidget(MultiWidget):
    """TODO: add docstring."""

    def __init__(self, attrs: Optional[Dict] = None):
        """TODO: add docstring."""
        attrs = {**attrs, **{'style': 'margin-right: 1rem'}} if attrs else {'style': 'margin-right: 1rem'}
        widgets = [
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Year'}}),
            forms.Select(attrs=attrs, choices=year_systems),
            forms.Select(attrs=attrs, choices=SEASONS),
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Month'}}),
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Day'}}),
            forms.TimeInput(attrs={**attrs, **{'placeholder': 'Time', 'class': 'vTimeField hidden'}}),
        ]
        super().__init__(widgets, attrs)

    def _parse_datetime_string(self, value: str) -> Tuple[int, ...]:
        """TODO: move elsewhere?"""
        year, month, day = value.split('-')
        hour, minute, second, microsecond = ('0', '0', '0', '0')
        if ' ' in day:
            day, time = day.split(' ')
            if ':' in time:
                hour, minute, second = time.split(':')
                if '.' in second:
                    second, microsecond = second.split('.')
        str_values = (year, month, day, hour, minute, second, microsecond)
        return tuple(int(string) for string in str_values)

    def decompress(self, value: Union[datetime, date, str, Any]):
        """
        This method takes a single “compressed” value from the field and returns a list of “decompressed” values.
        The input value can be assumed valid, but not necessarily non-empty.

        https://docs.djangoproject.com/en/3.1/ref/forms/widgets/#django.forms.MultiWidget.decompress
        """
        nones = (None, None, None, None, None, None)
        hour, minute, second, microsecond = 0, 0, 0, 0
        if not isinstance(value, HistoricDateTime):
            if isinstance(value, str):
                year, month, day, hour, minute, second, microsecond = self._parse_datetime_string(value)
            elif isinstance(value, (datetime, date)):
                year, month, day = value.year, value.month, value.day
                if isinstance(value, datetime):
                    hour, minute, second, microsecond = (
                        value.hour, value.minute, value.second, value.microsecond
                    )
            else:
                return nones
            # Convert value to HistoricDateTime
            value = HistoricDateTime(year, month, day, hour, minute, second, microsecond)
        return self._decompress_historic_datetime(value)

    @staticmethod
    def _decompress_historic_datetime(value: HistoricDateTime) -> List:
        year = value.year
        season, month, day, time = None, None, None, None
        hour, minute, second = value.hour, value.minute, value.second
        if value.use_ybp:
            year, year_system = value.year_bp, YBP
        elif value.is_bce:
            year, year_system = value.year_bce, BCE
        else:
            year_system = CE
        if value.season_is_known:
            season = get_season_from_month(value.month)
            if value.month_is_known:
                month = value.month
                if value.day_is_known:
                    day = value.day
        if 0 in {hour, minute, second} or 1 in {hour, minute, second}:
            time = None
        else:
            time = value.strftime('%H:%M:%S.%f')
        return [year, year_system, season, month, day, time]

    def value_from_datadict(self, data, files, name) -> Optional[str]:
        """TODO: add docstring."""
        values = list(super().value_from_datadict(data, files, name))
        full_n_values = 6
        min_n_values = 3
        n_values = len(values)
        if n_values < min_n_values:
            raise ValueError(f'Wrong number of values to unpack: {len(values)}')
        elif n_values < full_n_values:
            diff = full_n_values - n_values
            for _ in range(0, diff):
                values.append(None)
        year, year_system, season, month, day, time = values
        if not year:
            return None

        # Figure out year
        year, second, microsecond = get_year(year, year_system)

        # Replace None with 0 where necessary
        month, day = month or 0, day or 0

        # Figure out date precision
        hour, minute = 0, 0
        if not season and not month:
            hour, minute, second = 1, 1, second or 1
        elif season and not month:
            month = get_month_from_season(season)
            hour, minute, second = 0, 1, second or 1
        elif month and not day:
            hour, minute, second = 0, 0, second or 1
        month, day = (month or '1'), (day or '1')

        # Build datetime obj
        year, month, day, hour, minute, second, microsecond = (
            int(arg) for arg in (year, month, day, hour, minute, second, microsecond)
        )
        dt = HistoricDateTime(year, month, day, hour, minute, second, microsecond=microsecond)

        # Get date-parsable string for db
        dt_string = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        # Ensure the year is 4 digits; add leading zeros if necessary
        incomplete_year_pattern = re.compile(r'^(\d{1,3})(-.+)')
        if incomplete_year_pattern.match(dt_string):
            match = incomplete_year_pattern.match(dt_string)
            year_string = match.group(1)
            year_string = f'{year_string:0>4}'
            dt_string = incomplete_year_pattern.sub(rf'{year_string}\g<2>', dt_string)
        return dt_string
