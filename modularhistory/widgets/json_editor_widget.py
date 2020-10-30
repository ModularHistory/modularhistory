from typing import Any, Dict, Iterable, Mapping

from django_json_widget.widgets import JSONEditorWidget as BaseJSONEditorWidget


class JSONEditorWidget(BaseJSONEditorWidget):
    """Widget for editing JSON values."""

    def __init__(self, attrs=None, mode='form', options=None, width=None, height=None):
        """Construct the JSON editor widget."""
        # Prevent use of django_json_widget's default height
        attrs = attrs or {'style': 'display: inline-block; width: 90%;'}

        super().__init__(
            attrs=attrs, mode=mode, options=options, width=width, height=height
        )

    def value_from_datadict(
        self, data: Dict[str, Any], files: Mapping[str, Iterable[Any]], name: str
    ) -> Any:
        """
        Process the value returned from the JSON editor.

        Return the value to be saved.
        """
        json_value = super().value_from_datadict(data, files, name)
        if isinstance(json_value, dict):
            return {
                attribute: attribute_value
                for attribute, attribute_value in json_value.items()
                if attribute_value is not None
            }
        return json_value
