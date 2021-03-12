"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

import django

from modularhistory.constants.environments import Environments

try:
    from modularhistory.linters import flake8 as lint_with_flake8
    from modularhistory.linters import mypy as lint_with_mypy
except ModuleNotFoundError:
    print('Skipped importing nonexistent linting modules.')
from modularhistory.utils import qa

from .command import command

django.setup()

from django.conf import settings  # noqa: E402


@command
def autoformat(context):
    """Safely run autoformatters against all Python files."""
    qa.autoformat(context)


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
def test(context, docker=False):
    """Run tests."""
    pytest_args = [
        '-v',
        '-n 7',
        # '-x',
        '--maxfail=2',
        # '--hypothesis-show-statistics',
    ]
    command = f'coverage run -m pytest {" ".join(pytest_args)}'
    if settings.ENVIRONMENT == Environments.DEV:
        input('Make sure the dev server is running, then hit Enter/Return.')
    print(command)
    if docker:
        context.run(
            'docker build -t modularhistory/modularhistory . && docker-compose up'
        )
    context.run(command)
    context.run('coverage combine')
