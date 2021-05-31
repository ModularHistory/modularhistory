"""Classes for forms and form fields."""

from django.contrib.postgres.forms import SimpleArrayField as BaseSimpleArrayField

# from apps.admin.widgets.historic_date_widget import HistoricDateWidget


class SimpleArrayField(BaseSimpleArrayField):
    """Array field."""

    def widget_attrs(self, widget):
        """Return the attributes to apply to the field widget."""
        attrs = super().widget_attrs(widget)
        class_attr = 'vTextField'
        additional_classes = attrs.get('class')
        if additional_classes:
            class_attr = f'{class_attr} {additional_classes}'
        attrs['class'] = class_attr
        return attrs
