from django.contrib.postgres.forms import (
    SimpleArrayField as BaseSimpleArrayField,
    # SplitArrayField
)
from django.forms import DateTimeField, FileField

from history.widgets.historic_date_widget import HistoricDateWidget
from history.widgets.source_file_input import SourceFileInput


class SimpleArrayField(BaseSimpleArrayField):
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['class'] = 'vTextField' + (f' {attrs.get("class")}' or '')
        return attrs


class SourceFileFormField(FileField):
    widget = SourceFileInput


class HistoricDateFormField(DateTimeField):
    widget = HistoricDateWidget
