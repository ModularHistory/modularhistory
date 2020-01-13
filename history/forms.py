from datetime import datetime, date
from typing import Dict, Optional, Union

from django import forms
from django.contrib.postgres.forms import (
    SimpleArrayField as BaseSimpleArrayField,
    # SplitArrayField
)
from django.forms import DateTimeField, MultiWidget


class SimpleArrayField(BaseSimpleArrayField):
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['class'] = 'vTextField' + (f' {attrs.get("class")}' or '')
        return attrs


class HistoricDateWidget(MultiWidget):
    def __init__(self, attrs: Optional[Dict] = None):
        # days = [(day, day) for day in range(1, 32)]
        # months = [(month, month) for month in range(1, 13)]
        # years = [(year, year) for year in range(datetime.now().year)]
        attrs = {'style': 'margin-right: 1rem'} if not attrs else {
            **attrs, **{'style': 'margin-right: 1rem'}
        }
        widgets = [
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Year'}}),
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Month'}}),
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Day'}}),
            forms.TimeInput(attrs={**attrs, **{'placeholder': 'Time', 'class': 'vTimeField'}}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Union[datetime, date, str]):
        if isinstance(value, datetime):
            return [value.year, value.month, value.day, value.time()]
        elif isinstance(value, date):
            return [value.year, value.month, value.day, '00:00']
        elif isinstance(value, str):
            year, month, day = value.split('-')
            day, time = day.split(' ')
            return [year, month, day, time]
        return [None, None, None, None]

    def value_from_datadict(self, data, files, name) -> Optional[str]:
        values = super().value_from_datadict(data, files, name)
        if len(values) == 4:
            year, month, day, time = values
        elif len(values == 3):
            year, month, day = values
            time = '00:00'
        else:
            raise ValueError(f'Wrong number of values to unpack: {len(values)}')
        if not year:
            return None
        month, day = (month or '1'), (day or '1')
        # A single date-parsable string is expected.
        return f'{year}-{month}-{day} {time}'


class HistoricDateFormField(DateTimeField):
    widget = HistoricDateWidget


class HistoricDateFormField2(DateTimeField):
    widget = HistoricDateWidget

    # def __init__(self, *args, **kwargs):
    #     fields = (
    #         forms.IntegerField(required=False),
    #         forms.IntegerField(required=False),
    #         forms.IntegerField(required=False),
    #         forms.TimeField(required=False),
    #     )
    #     super().__init__(
    #         fields=fields,
    #         require_all_fields=False, **kwargs
    #     )
    #
    # def compress(self, values):
    #     compressed_values = []
    #     for value in values:
    #         if value != '':
    #             print(f'{type(value)}: {value}', file=stderr)
    #             sleep(15)
    #             raise Exception(f'{value}')
    #             compressed_values.append(value)
    #     return compressed_values
