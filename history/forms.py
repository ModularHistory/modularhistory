# type: ignore
# TODO: remove above line after fixing typechecking
from django.contrib.postgres.forms import (
    SimpleArrayField as BaseSimpleArrayField,
    # SplitArrayField
)
from django.forms import DateTimeField, FileField, ValidationError

from history.widgets.historic_date_widget import HistoricDateWidget
from history.widgets.source_file_input import SourceFileInput


class SimpleArrayField(BaseSimpleArrayField):
    """TODO: add docstring."""

    def widget_attrs(self, widget):
        """TODO: add docstring."""
        attrs = super().widget_attrs(widget)
        attrs['class'] = 'vTextField' + (f' {attrs.get("class")}' or '')
        return attrs


class SourceFileFormField(FileField):
    """TODO: add docstring."""

    widget = SourceFileInput


class HistoricDateFormField(DateTimeField):
    """TODO: add docstring."""

    widget = HistoricDateWidget

    def clean(self, value):
        """TODO: add docstring."""
        return super().clean(value)
