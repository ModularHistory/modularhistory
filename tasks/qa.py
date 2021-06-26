"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

from typing import TYPE_CHECKING, Optional

import django

from core.utils import qa
from tasks.command import command

if TYPE_CHECKING:
    from invoke.context import Context

django.setup()


@command
def autoformat(context: 'Context', filepaths: Optional[str] = None):
    """Safely run autoformatters against all Python files."""
    # Note: If we were using Invoke directly, we could use the iterable flag feature:
    # http://docs.pyinvoke.org/en/stable/concepts/invoking-tasks.html?highlight=incrementable#iterable-flag-values
    # However, since we're doing some funky magic on @task (--> @command) to get
    # type annotations working, we can't give the @command decorator any arguments.
    # So, we are using sub-string parsing instead.
    qa.autoformat(context, filepaths=(filepaths.split(',') if filepaths else None))


@command
def lint(context: 'Context'):
    """Run linters."""
    # Run Flake8
    print('Running flake8...')
    context.run('flake8 .')

    # Run MyPy
    print('Running mypy...')
    context.run('mypy .')


@command
def test(context: 'Context', docker: bool = True, fail_fast: bool = False):
    """Run tests."""
    pytest_args = [
        '-v',
        '-n 7',
        '--maxfail=3',
        # '--hypothesis-show-statistics',
    ]
    if fail_fast:
        pytest_args.append('-x')
    command = f'coverage run -m pytest {" ".join(pytest_args)}'
    print(command)
    if docker:
        context.run('docker-compose up -d dev')
    context.run(command)
    context.run('coverage combine')
