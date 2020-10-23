"""
Flake8 check.

https://docs.djangoproject.com/en/3.1/topics/checks/
"""

from typing import List, Optional

# from django.core.checks.messages import CheckMessage, DEBUG, INFO, WARNING, ERROR
from django.core.checks import register

from modularhistory.linters.flake8 import flake8 as _flake8


@register()
def flake8(app_configs: Optional[List], **kwargs) -> List:
    """Run flake8 linter."""
    _flake8(**kwargs)
    return []
