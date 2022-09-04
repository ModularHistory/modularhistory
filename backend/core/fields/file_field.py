"""ModularHistory's SourceFileField class."""

import logging
from functools import partial
from os.path import join
from typing import Callable

from django.conf import settings
from django.db.models import FileField, Model

from core.structures.source_file import TextualSourceFile


def _generate_upload_path(instance: Model, filename: str, path: str) -> str:
    if settings.DEBUG:
        logging.debug(
            f'Generating upload path for {filename} (associated with {instance})...'
        )
    filename = filename.replace(' ', '_')
    # TODO: dedupe
    return join(path, filename)


def upload_to(path: str) -> Callable:
    """
    Return the upload path for a file.

    The upload path is based on the relative media path (`path` arg, e.g. "sources" or "sources/").
    https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.FileField.upload_to
    """
    return partial(_generate_upload_path, path=path)


class SourceFileField(FileField):
    """TODO: add docstring."""

    attr_class = TextualSourceFile
