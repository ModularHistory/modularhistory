import os
from typing import Dict, Optional

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import MultiWidget, ClearableFileInput as BaseClearableFileInput

from history import settings
from history.structures.source_file import TextualSourceFile


class ClearableFileInput(BaseClearableFileInput):
    template_name = 'forms/clearable_file_input.html'


class SourceFileInput(MultiWidget):
    template_name = 'forms/source_file_input.html'

    def __init__(self, attrs: Optional[Dict] = None):
        file_choices = [(None, '-----')]
        for file_name in os.listdir(f'{settings.MEDIA_ROOT}/sources'):
            file_choices.append((f'sources/{file_name}', file_name))
        file_choices = ((value, string) for value, string in file_choices)
        widgets = [
            ClearableFileInput(attrs=attrs),
            forms.Select(attrs=attrs, choices=file_choices),
            forms.HiddenInput(),
            forms.HiddenInput(),
            forms.HiddenInput(),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Optional[TextualSourceFile]):
        if not value:
            return [None, None, None, None, None]
        ct = ContentType.objects.get_for_model(value.instance)
        return [value, value.name, value.name, ct.id, value.instance.id]

    def value_from_datadict(self, data, files, name) -> Optional[str]:
        values = super().value_from_datadict(data, files, name)
        if len(values) != 5:
            raise ValueError
        file, filepath, file_name, ct_id, instance_id = values
        if ct_id and instance_id:
            ct_id, instance_id = int(ct_id), int(instance_id)
            model_class = ContentType.objects.get_for_id(ct_id).model_class()
            instance = model_class.objects.get(id=instance_id)
            if hasattr(instance, 'file') and instance.file:
                file = instance.file
                file_name = file.name
                if filepath and filepath != file_name:
                    instance.file.name = filepath
                    instance.save()
        TextualSourceFile.dedupe()
        return file
