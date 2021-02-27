from glob import iglob
from typing import Iterable, Optional

from invoke.context import Context

CONTEXT = Context()


def autoformat(context: Context = CONTEXT, files: Optional[Iterable[str]] = None):
    """Autoformat all of ModularHistory's Python code."""
    commands = (
        (
            'autoflake --imports=apps,django,requests,typing,urllib3 '
            '--ignore-init-module-imports --in-place {filename}'
        ),
        ('unify --in-place {filename}'),
        ('black {filename}'),
    )
    file_names = files or iglob('[!.]**/*.py', recursive=True)
    for filename in file_names:
        print(f'Formatting {filename}...')
        for command in commands:
            context.run(command.format(filename=filename))
    context.run('isort .')
