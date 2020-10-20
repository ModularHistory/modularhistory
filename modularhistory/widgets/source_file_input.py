"""Form widgets for source files."""

import os
from typing import Dict, List, Optional, Tuple

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import ClearableFileInput as BaseClearableFileInput, MultiWidget

from modularhistory import settings
from modularhistory.structures.source_file import TextualSourceFile

Choice = Tuple[Optional[str], str]


class ClearableFileInput(BaseClearableFileInput):
    """TODO: add docstring."""

    template_name = 'forms/clearable_file_input.html'


class SourceFileInput(MultiWidget):
    """TODO: add docstring."""

    template_name = 'forms/source_file_input.html'

    def __init__(self, attrs: Optional[Dict] = None):
        """TODO: add docstring."""
        file_choices: List[Choice] = [(None, '-----')]
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

    def decompress(self, source_file: Optional[TextualSourceFile]):
        """TODO: add docstring."""
        if not source_file:
            return [None, None, None, None, None]
        ct = ContentType.objects.get_for_model(source_file.instance)
        return [source_file, source_file.name, source_file.name, ct.pk, source_file.instance.pk]

    def value_from_datadict(self, datadict, files, name) -> Optional[str]:
        """TODO: add docstring."""
        decompressed_values = super().value_from_datadict(datadict, files, name)
        if len(decompressed_values) != 5:
            raise ValueError
        source_file, filepath, file_name, ct_id, instance_id = decompressed_values
        if ct_id and instance_id:
            ct_id, instance_id = int(ct_id), int(instance_id)
            model_class = ContentType.objects.get_for_id(ct_id).model_class()
            instance = model_class.objects.get(id=instance_id)
            if getattr(instance, 'db_file', None):
                source_file = instance.db_file
                file_name = source_file.name
                if filepath and filepath != file_name:
                    instance.db_file.name = filepath
                    instance.save()
        TextualSourceFile.dedupe()
        return source_file
