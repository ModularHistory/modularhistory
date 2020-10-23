# monkeypatch.py
from inspect import ArgSpec, getfullargspec
from unittest.mock import patch

import invoke


def fix_annotations():
    """
    Fix Pyinvoke to accept annotations.

    Based on: https://github.com/pyinvoke/invoke/pull/606
    """

    def patched_inspect_getargspec(func):
        spec = getfullargspec(func)
        return ArgSpec(*spec[:4])

    org_task_argspec = invoke.tasks.Task.argspec

    def patched_task_argspec(*args, **kwargs):
        with patch(target='inspect.getargspec', new=patched_inspect_getargspec):
            return org_task_argspec(*args, **kwargs)

    invoke.tasks.Task.argspec = patched_task_argspec
    return True
