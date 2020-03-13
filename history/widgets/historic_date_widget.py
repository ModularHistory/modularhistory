from datetime import datetime, date
from decimal import Decimal, getcontext
from typing import Dict, Optional, Union
import re
from django import forms
from django.forms import MultiWidget
from sigfig import round

from history.structures.historic_datetime import (
    seasons, get_month_from_season,
    get_season_from_month, HistoricDateTime
)
from typing import Optional, Tuple

year_systems = (
    ('CE', 'CE'),
    ('BCE', 'BCE'),
    ('YBP', 'YBP')
)


def get_year(year: int, year_system: str = 'CE') -> Tuple[int, int, int]:
    year = int(year)
    if year > HistoricDateTime.bce_threshold and not year_system == 'YBP':
        # Safe to assume this should be YBP
        print(f'Using YBP year system instead of {year_system} ...')
        year_system = 'YBP'
    microsecond, second = 0, 0
    if year_system not in ('CE', 'BCE', 'YBP'):
        raise ValueError
    elif year_system == 'CE':
        pass  # default
    else:
        significant_figures = 4
        getcontext().prec = significant_figures
        year = year if year_system == 'BCE' else Decimal(year - 1950)
        year = round(year, sigfigs=HistoricDateTime.significant_figures)
        # Build a year stamp with max 6 digits
        scientific_notation: str = '{:.4e}'.format(year)  # '1.3800e+10' for the Big Bang
        decimal_num, exponent = scientific_notation.split('e+')
        exponent, decimal_num = int(exponent), int(decimal_num.replace('.', ''))  # 10, 13800 for the Big Bang
        inv_exponent = 30 - exponent  # 20 for the Big Bang
        inv_decimal_num = 100000 - int(decimal_num)  # 986200 for the Big Bang
        second, microsecond = inv_exponent, inv_decimal_num
        year = 1
        # TODO
        # if year_system == 'BCE':
        #     pass
        # elif year_system == 'YBP':
        #     pass
    return year, second, microsecond


class YearInput(MultiWidget):
    template_name = 'forms/year_input.html'

    def __init__(self, attrs: Optional[Dict] = None):
        attrs = attrs or {'class': 'form-control'}
        widgets = [
            forms.NumberInput(attrs={**attrs, **{'min': '1', 'class': 'form-control'}}),
            forms.Select(attrs=attrs, choices=year_systems),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Union[HistoricDateTime, int, str]):
        year, year_system = (None, None)
        if isinstance(value, HistoricDateTime):
            if value.use_ybp:
                year, year_system = value.year_bp, 'YBP'
            elif value.is_bce:
                year, year_system = value.year_bce, 'BCE'
            else:
                year, year_system = year, 'CE'
        elif value:
            return [value, 'CE']
        return [year, year_system]

    def value_from_datadict(self, data, files, name) -> Optional[str]:
        values = super().value_from_datadict(data, files, name)
        if len(values) != 2:
            raise ValueError(f'Wrong number of values to unpack: {len(values)}')
        year, year_system = values
        if not year:
            return None
        year, second, microsecond = get_year(year, year_system)
        # Build datetime object
        dt = HistoricDateTime(year, 1, 1, 1, 1, second, microsecond=microsecond)
        # Return date-parsable string for db
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


class HistoricDateWidget(MultiWidget):
    def __init__(self, attrs: Optional[Dict] = None):
        attrs = {'style': 'margin-right: 1rem'} if not attrs else {
            **attrs, **{'style': 'margin-right: 1rem'}
        }
        widgets = [
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Year'}}),
            forms.Select(attrs=attrs, choices=year_systems),
            forms.Select(attrs=attrs, choices=seasons),
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Month'}}),
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Day'}}),
            forms.TimeInput(attrs={**attrs, **{'placeholder': 'Time', 'class': 'vTimeField hidden'}}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Union[datetime, date, str]):
        year, year_system, season, month, day, time = (None, None, None, None, None, None)
        hour, minute, second, microsecond = None, None, None, None
        if isinstance(value, (datetime, date, str)):
            if isinstance(value, (datetime, date)):
                year, month, day = value.year, value.month, value.day
                season = get_season_from_month(month)
                if isinstance(value, datetime):
                    hour, minute, second, microsecond = (
                        value.hour, value.minute, value.second, value.microsecond
                    )
                    time = value.strftime('%H:%M:%S.%f')
            elif isinstance(value, str):
                year, month, day = value.split('-')
                hour, minute, second, microsecond = (0, 0, 0, 0)
                if ' ' in day:
                    day, time = day.split(' ')
                    hour, minute, second = time.split(':') if ':' in time else (0, 0, 0, 0)
                    second, microsecond = second.split('.') if '.' in second else (second, 0)
                year, month, day, hour, minute, second, microsecond = (
                    int(i) for i in (year, month, day, hour, minute, second, microsecond)
                )
            if not isinstance(value, HistoricDateTime):
                value = HistoricDateTime(
                    year, month, day,
                    hour or 0,
                    minute or 0,
                    second or 0,
                    microsecond or 0
                )
            if value.use_ybp:
                year, year_system = value.year_bp, 'YBP'
            elif value.is_bce:
                year, year_system = value.year_bce, 'BCE'
            else:
                year, year_system = year, 'CE'
            if not value.day_is_known:
                day = None
                if not value.month_is_known:
                    month = None
                    if not value.season_is_known:
                        season = None
            if 0 in (hour, minute, second) or 1 in (hour, minute, second):
                time = None
            return [year, year_system, season, month, day, time]
        return [None, None, None, None, None, None]

    def value_from_datadict(self, data, files, name) -> Optional[str]:
        values = super().value_from_datadict(data, files, name)
        if len(values) not in (6, 5, 4, 3):
            raise ValueError(f'Wrong number of values to unpack: {len(values)}')
        year, year_system, season, month, day, time = (
            None, None, None, 0, 0, None
        )
        if len(values) == 6:
            year, year_system, season, month, day, time = values
        elif len(values) == 5:
            year, season, month, day, time = values
        elif len(values) == 4:
            year, month, day, time = values
        elif len(values == 3):
            year, month, day = values
            time = '00:00:00'
        if not year:
            return None

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
        month, day = (month or '1'), (day or '1')

        # Build datetime object
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
