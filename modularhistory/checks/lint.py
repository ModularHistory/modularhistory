"""
MyPy static typing check.

See https://docs.djangoproject.com/en/3.1/topics/checks/.
"""

# import asyncio
from typing import List, Optional

# from asgiref.sync import sync_to_async
from django.core.checks import register

from modularhistory.linters.flake8 import flake8
from modularhistory.linters.mypy import mypy

# from django_q.tasks import async_task


def print_result(task):
    print(task.result)


@register()
def lint(app_configs: Optional[List] = None, **kwargs) -> List:
    """Run mypy as a check before executing management commands."""
    # async_task(flake8, hook=print_result)
    # async_task(mypy, hook=print_result)
    flake8()
    mypy()
    # asyncio.create_task(sync_to_async(flake8(**kwargs), thread_sensitive=False))
    # asyncio.create_task(sync_to_async(mypy(**kwargs), thread_sensitive=False))
    return []
