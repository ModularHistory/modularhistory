"""Form widgets for source files."""

import os
from typing import Dict, List, Optional, Tuple

from django import forms
from django.forms import ClearableFileInput as BaseClearableFileInput, MultiWidget

from modularhistory import settings
from modularhistory.structures.source_file import TextualSourceFile

Choice = Tuple[Optional[str], str]


class ClearableFileInput(BaseClearableFileInput):
    """Clearable file input widget."""

    template_name = 'forms/clearable_file_input.html'


class SourceFileInput(MultiWidget):
    """Widget for inputting or selecting a source file."""

    template_name = 'forms/source_file_input.html'

    def __init__(self, attrs: Optional[Dict] = None):
        """Construct the widget."""
        file_choices: List[Choice] = [(None, '-----')]
        for file_name in os.listdir(os.path.join(settings.MEDIA_ROOT, 'sources')):
            file_choices.append((file_name, file_name))
        widgets = [
            ClearableFileInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=file_choices),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, source_file: Optional[TextualSourceFile]):
        """Decompress a source file object into the values used in the widget."""
        if not source_file:
            return [None, None]
        return [source_file, source_file.name]

    def value_from_datadict(self, datadict, files, name) -> Optional[str]:
        """Compress values from the widget into a format that can be saved."""
        decompressed_values = super().value_from_datadict(datadict, files, name)
        if len(decompressed_values) != 2:
            raise ValueError
        source_file, file_name = decompressed_values
        if file_name and not source_file:
            source_file = os.path.join('sources', file_name)
        return source_file
