from typing import Iterable, Optional

try:
    from autohooks.api.git import get_staged_status, stash_unstaged_changes
except ModuleNotFoundError:
    print('Skipped importing nonexistent autohooks module.')
    get_staged_status, stash_unstaged_changes = None, None
from django.conf import settings
from invoke.context import Context

CONTEXT = Context()


def autoformat(
    context: Context = CONTEXT,
    filepaths: Optional[Iterable[str]] = None,
    staged: bool = False,
):
    """Autoformat Python code."""
    if get_staged_status is not None and stash_unstaged_changes is not None:
        pass
    else:
        print('Cannot autoformat; missing required autohooks module.')
    commands = [
        # https://isort.readthedocs.io/en/latest/
        'isort',
        # https://github.com/psf/black
        'black -S -q',
        # https://github.com/myint/autoflake
        'autoflake --imports=apps,django,requests,typing,urllib3 --ignore-init-module-imports -i -r',  # noqa: E501
    ]
    filepaths: Iterable[str] = filepaths or []
    if staged:
        staged_filepaths = get_staged_status()
        filepaths += staged_filepaths
    filepaths = [filepath for filepath in filepaths if filepath.endswith('.py')]
    if filepaths:
        commands.append('unify --in-place')  # does not support recursion (directories)
    if staged:
        if not filepaths:
            return
        with stash_unstaged_changes(staged_filepaths):
            for filepath in filepaths:
                for command in commands:
                    context.run(f'{command} {filepath}', warn=True)
    elif filepaths:
        for filepath in filepaths:
            for command in commands:
                context.run(f'{command} {filepath}', warn=True)
    else:
        with context.cd(settings.BASE_DIR):
            for command in commands:
                context.run(f'{command} .')
