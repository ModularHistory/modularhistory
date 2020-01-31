import os
from datetime import datetime, date
from typing import Dict, Optional, Union

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import MultiWidget, ClearableFileInput

from history import settings
from history.structures.historic_datetime import seasons, get_month_from_season, get_season_from_month, HistoricDateTime
from history.structures.source_file import SourceFile, file_name_pattern


class SourceFileInput(MultiWidget):

    def __init__(self, attrs: Optional[Dict] = None):
        attrs = attrs or {'style': ''}
        widgets = [
            ClearableFileInput(attrs=attrs),
            forms.NumberInput(attrs={**attrs, **{'placeholder': 'page offset'}}),
            forms.HiddenInput(),
            forms.HiddenInput(),
            forms.HiddenInput(),
            # forms.TimeInput(attrs={**attrs, **{'placeholder': 'Time', 'class': 'vTimeField'}}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Optional[SourceFile]):
        if not value:
            return [None, None, None, None, None]
        page_offset = None
        match = file_name_pattern.match(value.name)
        if match:
            page_offset = int(match.group(1))
        ct = ContentType.objects.get_for_model(value.instance)
        return [value, page_offset, value.name, ct.id, value.instance.id]

    def value_from_datadict(self, data, files, name) -> Optional[str]:
        values = super().value_from_datadict(data, files, name)
        if len(values) != 5:
            raise ValueError
        file, page_offset, file_name, ct_id, instance_id = values
        if page_offset:
            if isinstance(file, InMemoryUploadedFile):
                try:
                    current_page_offset = file_name_pattern.match(file_name).group(1)
                    if str(page_offset) != str(current_page_offset):
                        file_name = file_name.replace(f'_{current_page_offset}_', f'_{page_offset}_')
                except AttributeError as e:
                    file_name = f'_{page_offset}_{file_name}'
                file.name = file_name
            elif ct_id and instance_id:
                ct_id, instance_id = int(ct_id), int(instance_id)
                model_class = ContentType.objects.get_for_id(ct_id).model_class()
                instance = model_class.objects.get(id=instance_id)
                if hasattr(instance, 'file'):
                    file = instance.file
                    file_name = file.name
                    try:
                        current_page_offset = file_name_pattern.match(file_name).group(1)
                        if str(page_offset) != str(current_page_offset):
                            file_name = file_name.replace(f'_{current_page_offset}_.pdf', f'_{page_offset}_.pdf')
                    except AttributeError as e:
                        file_name = file_name.replace('.pdf', f'_{page_offset}_.pdf')
                    except Exception as e:
                        print(f'>>>>> {type(e).__name__}: {e}')
                        file_name = file_name.replace('.pdf', f'_{page_offset}_.pdf')
                    if file_name != file.name:
                        try:
                            os.rename(f'{settings.MEDIA_ROOT}/{file.name}', f'{settings.MEDIA_ROOT}/{file_name}')
                        except Exception as e:
                            print(f'>>>>> {type(e).__name__}: {e}')
                        instance.file.name = file_name
                        instance.save()
        SourceFile.dedupe()
        return file


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
            forms.Select(attrs=attrs, choices=seasons),
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Month'}}),
            forms.TextInput(attrs={**attrs, **{'placeholder': 'Day'}}),
            forms.TimeInput(attrs={**attrs, **{'placeholder': 'Time', 'class': 'vTimeField'}}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Union[datetime, date, str]):
        year, season, month, day, time, hour, minute, second = None, None, None, None, None, None, None, None
        if isinstance(value, (datetime, date, str)):
            if isinstance(value, (datetime, date)):
                year, month, day = value.year, value.month, value.day
                season = get_season_from_month(month)
                if isinstance(value, datetime):
                    hour, minute, second = value.hour, value.minute, value.second
                    time = value.strftime('%H:%M:%S')
            elif isinstance(value, str):
                year, month, day = value.split('-')
                time = (0, 0, 0)
                if ' ' in day:
                    day, time = day.split(' ')
                    time = time.split(':') if ':' in time else (0, 0, 0)
                hour, minute, second = time
                year, month, day, hour, minute, second = (int(i) for i in (year, month, day, hour, minute, second))
            if not isinstance(value, HistoricDateTime):
                try:
                    value = HistoricDateTime(year, month, day, hour or 0, minute or 0, second or 0)
                except Exception as e:
                    for x in (year, month, day, hour, minute, second):
                        print(x)
                    raise
            if not value.day_is_known:
                day = None
                if not value.month_is_known:
                    month = None
                    if not value.season_is_known:
                        season = None
            if 0 in (hour, minute, second) or 1 in (hour, minute, second):
                time = None
            return [year, season, month, day, time]
        return [None, None, None, None, None]

    def value_from_datadict(self, data, files, name) -> Optional[str]:
        season = None
        values = super().value_from_datadict(data, files, name)
        if len(values) == 5:
            year, season, month, day, time = values
        elif len(values) == 4:
            year, month, day, time = values
        elif len(values == 3):
            year, month, day = values
            time = '00:00:00'
        else:
            raise ValueError(f'Wrong number of values to unpack: {len(values)}')
        if month:
            season = get_season_from_month(month)
        if not year:
            return None
        elif not season:
            time = '01:01:01'
        elif season and not month:
            month = get_month_from_season(season)
            time = '00:01:01'
        elif month and not day:
            time = '00:00:01'
        month, day = (month or '1'), (day or '1')
        # A single date-parsable string is expected.
        return f'{year}-{month}-{day} {time}'
