"""See Invoke's documentation: http://docs.pyinvoke.org/en/stable/."""

from inspect import ArgSpec, getfullargspec
from typing import Any, Callable, TypeVar
from unittest.mock import patch

import invoke


def fix_annotations():
    """
    Fix PyInvoke to accept annotations.

    Based on: https://github.com/pyinvoke/invoke/pull/606
    """

    def patched_inspect_getargspec(func):  # noqa: ANN001,ANN201
        spec = getfullargspec(func)
        return ArgSpec(*spec[:4])

    org_task_argspec = invoke.tasks.Task.argspec

    def patched_task_argspec(*args, **kwargs):  # noqa: ANN001,ANN201
        with patch(target='inspect.getargspec', new=patched_inspect_getargspec):
            return org_task_argspec(*args, **kwargs)

    invoke.tasks.Task.argspec = patched_task_argspec


fix_annotations()

TaskFunction = TypeVar('TaskFunction', bound=Callable[..., Any])


def command(task_function: TaskFunction) -> TaskFunction:
    """Wrap invoke.task to enable type annotations."""
    task_function.__annotations__ = {}
    return invoke.task(task_function)
