"""https://docs.djangoproject.com/en/3.1/topics/checks/"""

import re
import subprocess
from sys import stderr
# from os import path
from typing import List, Optional, Sequence, Union

# from django.core.checks.messages import CheckMessage, DEBUG, INFO, WARNING, ERROR
from django.core.checks import register

MultiOptions = Union[Sequence[str], str]

CONFIG_FILE = 'setup.cfg'

# Example:
# ./history/fields/html_field.py:138:17: WPS442 Found outer scope names shadowing: Quote
OUTPUT_PATTERN = re.compile(r'^(.+\d+): (\w+\d+)\s+(.+)')


@register()
def flake8(app_configs: Optional[List], **kwargs) -> List:
    """."""
    print()
    proc = subprocess.Popen(f'flake8', stdout=subprocess.PIPE)
    _output, _err = proc.communicate()
    output = _output.decode()
    output_lines = output.rstrip().split('\n')
    for line in output_lines:
        parsed_line = OUTPUT_PATTERN.match(line)
        if not parsed_line:
            print(line, end='')
            continue
        location = parsed_line.group(1)
        code = parsed_line.group(2)
        message = parsed_line.group(3)
        print(f'{location}: {code}: {message}')
    return []
