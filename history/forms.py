from django.contrib.postgres.forms import (
    SimpleArrayField as BaseSimpleArrayField,
    # SplitArrayField
)
from django.forms import DateTimeField, FileField

from history.widgets import HistoricDateWidget, SourceFileInput


class SimpleArrayField(BaseSimpleArrayField):
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['class'] = 'vTextField' + (f' {attrs.get("class")}' or '')
        return attrs


class SourceFileFormField(FileField):
    widget = SourceFileInput


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
