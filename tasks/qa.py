"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

from typing import Optional

import django

try:
    from core.linters import flake8 as lint_with_flake8
    from core.linters import mypy as lint_with_mypy
except ModuleNotFoundError:
    print('Skipped importing nonexistent linting modules.')
from core.utils import qa

from .command import command

django.setup()


@command
def autoformat(context, filepaths: Optional[str] = None):
    """Safely run autoformatters against all Python files."""
    # Note: If we were using Invoke directly, we could use the iterable flag feature:
    # http://docs.pyinvoke.org/en/stable/concepts/invoking-tasks.html?highlight=incrementable#iterable-flag-values
    # However, since we're doing some funky magic on @task (--> @command) to get
    # type annotations working, we can't give the @command decorator any arguments.
    # So, we are using sub-string parsing instead.
    qa.autoformat(context, filepaths=(filepaths.split(',') if filepaths else None))


@command
def flake8(context, *args):
    """Run flake8 linter."""
    lint_with_flake8(interactive=True)


@command
def mypy(context, *args):
    """Run mypy static type checker."""
    lint_with_mypy()


@command
def lint(context, *args):
    """Run linters."""
    # Run Flake8
    print('Running flake8...')
    lint_with_flake8(interactive=True)

    # Run MyPy
    print('Running mypy...')
    lint_with_mypy()


@command
def test(context, docker: bool = True):
    """Run tests."""
    pytest_args = [
        '-v',
        '-n 7',
        # '-x',
        '--maxfail=2',
        # '--hypothesis-show-statistics',
    ]
    command = f'coverage run -m pytest {" ".join(pytest_args)}'
    print(command)
    if docker:
        context.run('docker-compose up -d dev')
    context.run(command)
    context.run('coverage combine')
