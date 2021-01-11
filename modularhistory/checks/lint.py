"""
MyPy static typing check.

See https://docs.djangoproject.com/en/3.1/topics/checks/.
"""

from typing import List, Optional

from django.core.checks import register

from modularhistory.linters.flake8 import flake8
from modularhistory.linters.mypy import mypy


def print_result(task):
    """Print the task result."""
    print(task.result)


@register()
def lint(app_configs: Optional[List] = None, **kwargs) -> List:
    """Run mypy as a check before executing management commands."""
    flake8()
    mypy()
    return []
