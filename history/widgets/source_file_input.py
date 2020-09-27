"""Form widgets for source files."""

import os
from typing import Dict, List, Optional, Tuple

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import MultiWidget, ClearableFileInput as BaseClearableFileInput

from history import settings
from history.structures.source_file import TextualSourceFile


class ClearableFileInput(BaseClearableFileInput):
    """TODO: add docstring."""

    template_name = 'forms/clearable_file_input.html'


class SourceFileInput(MultiWidget):
    """TODO: add docstring."""

    template_name = 'forms/source_file_input.html'

    def __init__(self, attrs: Optional[Dict] = None):
        """TODO: add docstring."""
        file_choices: List[Tuple[Optional[str], str]] = [(None, '-----')]
        for file_name in os.listdir(os.path.join(settings.MEDIA_ROOT, 'sources')):
            file_choices.append((f'sources/{file_name}', file_name))
        widgets = [
            ClearableFileInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=file_choices),
            forms.HiddenInput(),
            forms.HiddenInput(),
            forms.HiddenInput(),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Optional[TextualSourceFile]):
        """TODO: add docstring."""
        if not value:
            return [None, None, None, None, None]
        ct = ContentType.objects.get_for_model(value.instance)
        return [value, value.name, value.name, ct.id, value.instance.id]

    def value_from_datadict(self, data, files, name) -> Optional[str]:
        """TODO: add docstring."""
        values = super().value_from_datadict(data, files, name)
        if len(values) != 5:
            raise ValueError
        file, filepath, file_name, ct_id, instance_id = values
        if ct_id and instance_id:
            ct_id, instance_id = int(ct_id), int(instance_id)
            model_class = ContentType.objects.get_for_id(ct_id).model_class()
            instance = model_class.objects.get(id=instance_id)
            if getattr(instance, 'db_file', None):
                file = instance.db_file
                file_name = file.name
                if filepath and filepath != file_name:
                    instance.db_file.name = filepath
                    instance.save()
        TextualSourceFile.dedupe()
        return file
