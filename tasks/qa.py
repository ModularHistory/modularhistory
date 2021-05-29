"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

from typing import Optional

import django

try:
    from core.linters import flake8 as lint_with_flake8
    from core.linters import mypy as lint_with_mypy
except ModuleNotFoundError:
    print('Skipped importing nonexistent linting modules.')
from typing import TYPE_CHECKING

from core.utils import qa

from .command import command

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
def flake8(context: 'Context', *args):
    """Run flake8 linter."""
    lint_with_flake8(interactive=True)


@command
def mypy(context: 'Context', *args):
    """Run mypy static type checker."""
    lint_with_mypy()


@command
def lint(context: 'Context', *args):
    """Run linters."""
    # Run Flake8
    print('Running flake8...')
    lint_with_flake8(interactive=True)

    # Run MyPy
    print('Running mypy...')
    lint_with_mypy()


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
