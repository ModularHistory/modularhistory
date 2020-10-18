"""
ModularHistory's checks.

See https://docs.djangoproject.com/en/3.1/topics/checks/.
"""

from .mypy import mypy
from .flake8 import flake8
