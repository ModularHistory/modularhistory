# type: ignore
# TODO: remove above line after fixing typechecking
import os
from functools import partial
from os.path import isfile, join
from typing import Callable, Optional

from django.db.models import FileField, Model
from django.forms import Field

from history import settings
from history.forms import SourceFileFormField
from history.structures.source_file import TextualSourceFile


def dedupe_files(path: str, new_file_name: Optional[str] = None):
    """TODO: add docstring."""
    # TODO: implement file dedupe for cloud storage
    if not settings.IS_GCP:
        full_path = join(settings.MEDIA_ROOT, path)
        if not new_file_name:
            raise NotImplementedError
        else:
            # If uploading a new file, replace an older version if one exists.
            # TODO: Ensure this doesn't result in replacements of unrelated files that happen to have the same name.
            new_file_name, extension = os.path.splitext(new_file_name)
            file_names = []
            for f in os.listdir(full_path):
                if isfile(join(full_path, f)) and extension in f:
                    file_name = f.replace(extension, '')
                    file_names.append(file_name)
            to_remove = []
            for file_name in file_names:
                if file_name == new_file_name:
                    full_file_name = f'{file_name}{extension}'
                    file_path = join(path, full_file_name)
                    to_remove.append(file_path)
            for file_path in to_remove:
                print(f'Removing old version of {file_path} ...')
                os.remove(join(settings.MEDIA_ROOT, file_path))


def _generate_upload_path(instance: Model, filename: str, path: str) -> str:
    if settings.DEBUG:
        print(f'Generating upload path for {filename} (associated with {instance})...')
    path, filename = path, filename
    filename = filename.replace(' ', '_')
    dedupe_files(path, new_file_name=filename)
    return join(path, filename)


def upload_to(path: str) -> Callable:
    """
    Return the upload path, based on the relative media path (`path` arg, e.g. "sources" or "sources/").
    https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.FileField.upload_to
    """
    return partial(_generate_upload_path, path=path)


class SourceFileField(FileField):
    attr_class = TextualSourceFile

    def formfield(self, **kwargs) -> Field:
        return super(FileField, self).formfield(**{
            'form_class': SourceFileFormField,
            **kwargs,
        })
