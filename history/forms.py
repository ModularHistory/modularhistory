"""Classes for forms and form fields."""

from django.contrib.postgres.forms import (
    SimpleArrayField as BaseSimpleArrayField,
    # SplitArrayField
)
from django.forms import DateTimeField, FileField

from history.widgets.historic_date_widget import HistoricDateWidget
from history.widgets.source_file_input import SourceFileInput


class SimpleArrayField(BaseSimpleArrayField):
    """TODO: add docstring."""

    def widget_attrs(self, widget):
        """TODO: add docstring."""
        attrs = super().widget_attrs(widget)
        class_attr = 'vTextField'
        additional_classes = attrs.get('class')
        if additional_classes:
            class_attr = f'{class_attr} {additional_classes}'
        attrs['class'] = class_attr
        return attrs


class SourceFileFormField(FileField):
    """TODO: add docstring."""

    widget = SourceFileInput


class HistoricDateFormField(DateTimeField):
    """TODO: add docstring."""

    widget = HistoricDateWidget
