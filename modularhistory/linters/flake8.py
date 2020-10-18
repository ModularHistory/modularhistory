"""
Module for Flake8 check.

https://docs.djangoproject.com/en/3.1/topics/checks/
"""

import re
import subprocess
from typing import Dict, Optional, Union

from modularhistory.linters import utils

StringOrDict = Union[str, Dict[str, str]]

# Example:
# ./history/fields/html_field.py:138:17: WPS442 Found outer scope names shadowing: Quote
OUTPUT_PATTERN = re.compile(r'^(.+\d+): (\w+\d+)\s+(.+)')


def flake8(**kwargs):
    """Runs flake8 linter."""
    print()
    proc = subprocess.Popen('flake8', stdout=subprocess.PIPE, shell=False)
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
        explanation_url = get_violation_explanation_url(code)
        print(f'{location}: {utils.colored(message, color="red")}  [{code}: {explanation_url}]')
    print()


VIOLATION_DEFAULT_URL = 'https://wemake-python-stylegui.de/en/latest/pages/usage/violations'
VIOLATION_EXPLANATION_URLS: Dict[str, StringOrDict] = {
    'B': 'https://github.com/PyCQA/flake8-bugbear#list-of-warnings',  # Bugbear
    'C': {
        '4': 'https://github.com/adamchainz/flake8-comprehensions',  # Comprehensions
        '8': 'https://pypi.org/project/flake8-commas/',  # Commas
        '9': 'http://flake8.pycqa.org/en/latest/user/error-codes.html'  # McCabe
    },
    'D': 'https://www.pydocstyle.org/en/latest/error_codes.html',  # Docstrings
    'DAR': 'https://github.com/terrencepreilly/darglint#error-codes',  # Darglint
    'E800': 'https://github.com/sobolevn/flake8-eradicate',  # Eradicate
    'E': 'http://pycodestyle.pycqa.org/en/latest/intro.html#error-codes',  # Pycodestyle
    'W': 'http://pycodestyle.pycqa.org/en/latest/intro.html#error-codes',  # Pycodestyle
    'F': 'http://flake8.pycqa.org/en/latest/user/error-codes.html',  # Flake8
    'I': 'https://github.com/gforcada/flake8-isort',  # Isort
    'N800': 'https://github.com/sobolevn/flake8-broken-line',  # Broken line
    'N': {
        '8': 'https://github.com/PyCQA/pep8-naming'  # Pep8 naming
    },
    'P': {
        '1,2,3': 'https://github.com/xZise/flake8-string-format#error-codes',  # Flake8 string format
    },
    'Q': 'https://github.com/zheller/flake8-quotes',  # Quotes
    'RST': 'https://github.com/peterjc/flake8-rst-docstrings',  # RST docstrings
    'S': 'https://github.com/tylerwince/flake8-bandit',  # Bandit
    'T100': 'https://github.com/JBKahn/flake8-debugger/blob/master/flake8_debugger.py',  # Debugger
    'WPS': {
        '0': f'{VIOLATION_DEFAULT_URL}/system.html#system',
        '1': f'{VIOLATION_DEFAULT_URL}/naming.html#naming',
        '2': f'{VIOLATION_DEFAULT_URL}/complexity.html#complexity',
        '3': f'{VIOLATION_DEFAULT_URL}/consistency.html#consistency',
        '4': f'{VIOLATION_DEFAULT_URL}/best_practices.html#best-practices',
        '5': f'{VIOLATION_DEFAULT_URL}/refactoring.html#refactoring',
        '6': f'{VIOLATION_DEFAULT_URL}/oop.html#oop',
        '7,8,9': VIOLATION_DEFAULT_URL
    }
}


def get_violation_explanation_url(violation_code: str) -> str:
    """Return the violation explanation URL for the given violation code."""
    match = re.match(r'(\D+)(\d+)', violation_code)
    if not match:
        return VIOLATION_DEFAULT_URL
    prefix, number = match.group(1), match.group(2)
    url_match: Optional[StringOrDict]
    url_match = VIOLATION_EXPLANATION_URLS.get(violation_code)
    if isinstance(url_match, str):
        return url_match
    url_match = VIOLATION_EXPLANATION_URLS.get(prefix)
    if url_match:
        if isinstance(url_match, str):
            return url_match
        hundredth_place = number[0]
        submatch = url_match.get(hundredth_place)
        if not submatch:
            for key, value in url_match.items():
                if hundredth_place in key.split(','):
                    submatch = value
        if isinstance(submatch, str):
            return submatch
    return VIOLATION_DEFAULT_URL
