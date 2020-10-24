"""ModularHistory's SourceFileField class."""

import logging
import os
from functools import partial
from os.path import isfile, join
from typing import Callable, Optional

from django.db.models import FileField, Model
from django.forms import Field

from modularhistory import settings
from modularhistory.forms import SourceFileFormField
from modularhistory.structures.source_file import TextualSourceFile


def dedupe_files(path: str, new_file_name: Optional[str] = None):
    """Remove duplicate files."""
    # TODO: implement file dedupe for cloud storage
    if not settings.IS_GCP:
        full_path = join(settings.MEDIA_ROOT, path)
        if new_file_name:
            # If uploading a new file, replace an older version if one exists.
            # TODO: Ensure this doesn't result in replacements of unrelated files.
            new_file_name, extension = os.path.splitext(new_file_name)
            file_names = []
            for file_name in os.listdir(full_path):
                if isfile(join(full_path, file_name)) and extension in file_name:
                    file_names.append(file_name.replace(extension, ''))
            to_remove = []
            for extant_file_name in file_names:
                if extant_file_name == new_file_name:
                    full_file_name = f'{extant_file_name}{extension}'
                    file_path = join(path, full_file_name)
                    to_remove.append(file_path)
            for file_path in to_remove:
                logging.info(f'Removing old version of {file_path} ...')
                os.remove(join(settings.MEDIA_ROOT, file_path))
        else:
            raise NotImplementedError


def _generate_upload_path(instance: Model, filename: str, path: str) -> str:
    if settings.DEBUG:
        logging.info(
            f'Generating upload path for {filename} (associated with {instance})...'
        )
    filename = filename.replace(' ', '_')
    dedupe_files(path, new_file_name=filename)
    return join(path, filename)


def upload_to(path: str) -> Callable:
    """
    Return the upload path for a file.

    The upload path is based on the relative media path (`path` arg, e.g. "sources" or "sources/").
    https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.FileField.upload_to
    """
    return partial(_generate_upload_path, path=path)


class SourceFileField(FileField):
    """TODO: add docstring."""

    attr_class = TextualSourceFile

    def formfield(self, **kwargs) -> Field:
        """TODO: add docstring."""
        return super(FileField, self).formfield(
            **{
                'form_class': SourceFileFormField,
                **kwargs,
            }
        )
