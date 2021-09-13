from typing import Iterable, Optional

from django.conf import settings
from invoke.context import Context


def autoformat(
    context: Optional[Context] = None,
    filepaths: Optional[Iterable[str]] = None,
):
    """Autoformat Python code."""
    print(f'Autoformatting files: {filepaths=}')
    if context is None:
        context = Context()
    commands = [
        # https://isort.readthedocs.io/en/latest/
        'isort',
        # https://github.com/psf/black
        'black -S -q',
        # https://github.com/myint/autoflake
        'autoflake --imports=apps,django,requests,typing,urllib3 --ignore-init-module-imports -i -r',  # noqa: E501
    ]
    filepaths: Iterable[str] = filepaths or []
    filepaths = [filepath for filepath in filepaths if filepath.endswith('.py')]
    if filepaths:
        commands.append('unify --in-place')  # does not support recursion (directories)
        for filepath in filepaths:
            print(f'Autoformatting {filepath} ...')
            for command in commands:
                context.run(f'{command} {filepath}', warn=True)
    else:
        print('Autoformatting all Python code ...')
        with context.cd(settings.BASE_DIR):
            for command in commands:
                context.run(f'{command} .')
    print('Finished autoformatting Python code.')
