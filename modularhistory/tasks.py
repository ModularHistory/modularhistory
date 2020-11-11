"""Asynchronous tasks."""

import os
from getpass import getuser
from sys import stderr

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')


def _debug(self) -> None:
    """TODO: write docstring."""
    print('Debugging....')
    if hasattr(self, 'request'):
        print('Request: {0!r}'.format(self.request))
    print(f'User: {getuser()}', file=stderr)
