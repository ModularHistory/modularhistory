"""
MyPy static typing check.

See https://docs.djangoproject.com/en/3.1/topics/checks/.
"""

from typing import List, Optional

from django.core.checks import register

from modularhistory.linters.mypy import mypy as _mypy


@register()
def mypy(app_configs: Optional[List] = None, **kwargs) -> List:
    """Run mypy as a check before executing management commands."""
    _mypy(**kwargs)
    return []
