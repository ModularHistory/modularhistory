import os
from glob import iglob
from typing import Iterable, Optional

from django.conf import settings
from invoke.context import Context

CONTEXT = Context()


def autoformat(context: Context = CONTEXT, files: Optional[Iterable[str]] = None):
    """Autoformat all of ModularHistory's Python code."""
    with context.cd(settings.BASE_DIR):
        # https://isort.readthedocs.io/en/latest/
        context.run('isort .')
        # https://github.com/psf/black
        context.run('black -S -q .')
        # https://github.com/myint/autoflake
        context.run(
            'autoflake --imports=apps,django,requests,typing,urllib3 '
            '--ignore-init-module-imports -i -r .'
        )
    target_file_pattern = os.path.join(settings.BASE_DIR, '[!.]**/*.py')
    filepaths = files or iglob(target_file_pattern, recursive=True)
    for filepath in filepaths:
        context.run(f'unify --in-place {filepath}')
