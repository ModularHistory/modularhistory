from typing import Iterable, Optional

from autohooks.api.git import get_staged_status, stash_unstaged_changes
from django.conf import settings
from invoke.context import Context

CONTEXT = Context()


def autoformat(
    context: Context = CONTEXT,
    files: Optional[Iterable[str]] = None,
    staged: bool = False,
):
    """Autoformat all of ModularHistory's Python code."""
    commands = [
        # https://isort.readthedocs.io/en/latest/
        'isort',
        # https://github.com/psf/black
        'black -S -q',
        # https://github.com/myint/autoflake
        'autoflake --imports=apps,django,requests,typing,urllib3 --ignore-init-module-imports -i -r',  # noqa: E501
    ]
    if staged:
        files = get_staged_status()
        if not files:
            # no files to autoformat
            return 0
        commands.append('unify --in-place')  # does not support recursion (directories)
        with stash_unstaged_changes(files):
            for file in files:
                for command in commands:
                    context.run(f'{command} {file}', warn=True)
    else:
        with context.cd(settings.BASE_DIR):
            for command in commands:
                context.run(f'{command} .')
