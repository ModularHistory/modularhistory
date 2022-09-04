"""Classes for forms and form fields."""

from django.contrib.postgres.forms import SimpleArrayField as BaseSimpleArrayField


class SimpleArrayField(BaseSimpleArrayField):
    """Array field."""

    def widget_attrs(self, widget) -> dict:
        """Return the attributes to apply to the field widget."""
        attrs = super().widget_attrs(widget)
        class_attr = 'vTextField'
        additional_classes = attrs.get('class')
        if additional_classes:
            class_attr = f'{class_attr} {additional_classes}'
        attrs['class'] = class_attr
        return attrs
