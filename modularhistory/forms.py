"""Classes for forms and form fields."""

from django.contrib.postgres.forms import (
    SimpleArrayField as BaseSimpleArrayField,
    # SplitArrayField
)
from django.forms import DateTimeField, FileField

from modularhistory.widgets.historic_date_widget import HistoricDateWidget
from modularhistory.widgets.source_file_input import SourceFileInput


class SimpleArrayField(BaseSimpleArrayField):
    """Array field."""

    def widget_attrs(self, widget):
        """Returns the attributes to apply to the field widget."""
        attrs = super().widget_attrs(widget)
        class_attr = 'vTextField'
        additional_classes = attrs.get('class')
        if additional_classes:
            class_attr = f'{class_attr} {additional_classes}'
        attrs['class'] = class_attr
        return attrs


class SourceFileFormField(FileField):
    """Form field for source files."""

    widget = SourceFileInput


class HistoricDateFormField(DateTimeField):
    """Form field for historic datetimes (potentially BCE, with variable specificity."""

    widget = HistoricDateWidget
