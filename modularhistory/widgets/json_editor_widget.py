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
