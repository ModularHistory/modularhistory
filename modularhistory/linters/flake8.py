"""
Module for Flake8 check.

https://docs.djangoproject.com/en/3.1/topics/checks/
"""

import re
import subprocess  # noqa: S404
from typing import Callable, Dict, List, Optional, Tuple, Union

from modularhistory.linters.config import (
    ConfigFileOptionsParser as BaseConfigFileOptionsParser,
)
from modularhistory.linters.config import LinterOptions, PerModuleOptions
from modularhistory.utils import linting
from modularhistory.utils.qa import autoformat

StringOrCallable = Union[str, Callable]
StringOrCallableOrDict = Union[StringOrCallable, Dict[str, StringOrCallable]]

# Example:
# ./history/fields/html_field.py:138:17: WPS442 Found outer scope names shadowing: Quote
OUTPUT_PATTERN = re.compile(r'^(.+\d+): (\w+\d+)\s+(.+)')

AUTOFORMAT_TRIGGERS = {'BLK100', 'Q000'}


def flake8(interactive: bool = False, **kwargs):
    """Run flake8 linter."""
    output = subprocess.run(['flake8'], capture_output=True).stdout  # noqa: S603, S607
    if output:
        process_flake8_output(output.decode(), interactive=interactive)


def process_flake8_output(output: str, interactive: bool = False):
    """Process/filters and displays output from flake8."""
    options, per_module_options = _get_flake8_options()
    output_lines = output.rstrip().split('\n')

    files_to_autoformat = set()
    for line in output_lines:
        parsed_line = OUTPUT_PATTERN.match(line)
        if not parsed_line:
            print(line, end='')
            continue
        location = parsed_line.group(1)
        code = parsed_line.group(2)
        message = parsed_line.group(3)
        try:
            filename, _line_number = location.split(':')
        except ValueError:
            filename, _line_number = location.split(':')[:2]
        _process_flake8_message(location, filename, code, message, options)
        if code in AUTOFORMAT_TRIGGERS:
            files_to_autoformat.add(filename)


def _process_flake8_message(location, filename, code, message, options):
    if not options.error_is_ignored(message, code, filename):
        explanation_url = get_violation_explanation_url(code)
        print(
            f'{location}: {linting.colored(message, color="red")} '
            f' [{code}: {explanation_url}]'
        )


def _get_flake8_options() -> Tuple[LinterOptions, PerModuleOptions]:
    """Return an Options object to be used by mypy."""
    options = LinterOptions()
    module_options: List[Tuple[str, LinterOptions]] = []
    ConfigFileFlake8OptionsParser().apply(options, module_options)  # type: ignore
    return options, module_options


class ConfigFileFlake8OptionsParser(BaseConfigFileOptionsParser):
    """Config file options parser for mypy."""

    report_unrecognized_options = False

    def __init__(self, script_name: str = 'flake8'):
        """Construct the flake8 options parser."""
        super().__init__(script_name=script_name)


VIOLATION_DEFAULT_URL = (
    'https://wemake-python-stylegui.de/en/latest/pages/usage/violations'
)
VIOLATION_EXPLANATION_URLS: Dict[str, StringOrCallableOrDict] = {
    'B': 'https://github.com/PyCQA/flake8-bugbear#list-of-warnings',  # Bugbear
    'BLK': 'https://github.com/peterjc/flake8-black',  # Black
    'C': {
        '4': 'https://github.com/adamchainz/flake8-comprehensions',  # Comprehensions
        '8': 'https://pypi.org/project/flake8-commas/',  # Commas
        '9': 'http://flake8.pycqa.org/en/latest/user/error-codes.html',  # McCabe
    },
    'D': 'https://www.pydocstyle.org/en/latest/error_codes.html',  # Docstrings
    'DAR': 'https://github.com/terrencepreilly/darglint#error-codes',  # Darglint
    'DJ12': 'https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/#model-style',  # noqa: E501
    'DJ': 'https://github.com/rocioar/flake8-django',  # Flake8-Django
    'E800': 'https://github.com/sobolevn/flake8-eradicate',  # Eradicate
    'E': 'http://pycodestyle.pycqa.org/en/latest/intro.html#error-codes',
    'EXE': 'https://github.com/xuhdev/flake8-executable',
    'W': 'http://pycodestyle.pycqa.org/en/latest/intro.html#error-codes',
    'F': 'http://flake8.pycqa.org/en/latest/user/error-codes.html',  # Flake8
    'H': 'https://github.com/mschwager/cohesion',  # Cohesion
    'I': 'https://github.com/gforcada/flake8-isort',  # Isort
    'N400': 'https://github.com/sobolevn/flake8-broken-line',  # Broken line
    'N': {
        '8': 'https://github.com/PyCQA/pep8-naming',  # Pep8 naming
    },
    'P': {
        '1,2,3': 'https://github.com/xZise/flake8-string-format#error-codes',
    },
    'PT': 'https://github.com/m-burst/flake8-pytest-style/blob/master/docs/rules/{code}.md'.format,
    'Q': 'https://github.com/zheller/flake8-quotes',  # Quotes
    'RST': 'https://github.com/peterjc/flake8-rst-docstrings',  # RST docstrings
    'S': 'https://github.com/tylerwince/flake8-bandit',  # Bandit
    'SC': 'https://github.com/MichaelAquilina/flake8-spellcheck',
    'T100': 'https://github.com/JBKahn/flake8-debugger/blob/master/flake8_debugger.py',
    'WPS': {
        '0': f'{VIOLATION_DEFAULT_URL}/system.html#system',
        '1': f'{VIOLATION_DEFAULT_URL}/naming.html#naming',
        '2': f'{VIOLATION_DEFAULT_URL}/complexity.html#complexity',
        '3': f'{VIOLATION_DEFAULT_URL}/consistency.html#consistency',
        '4': f'{VIOLATION_DEFAULT_URL}/best_practices.html#best-practices',
        '5': f'{VIOLATION_DEFAULT_URL}/refactoring.html#refactoring',
        '6': f'{VIOLATION_DEFAULT_URL}/oop.html#oop',
        '7,8,9': VIOLATION_DEFAULT_URL,
    },
}


def get_violation_explanation_url(violation_code: str) -> str:  # noqa: C901
    """Return the violation explanation URL for the given violation code."""
    match, url = re.match(r'(\D+)(\d+)', violation_code), None
    if match:
        prefix, number = match.group(1), match.group(2)
        url_match: Optional[StringOrCallableOrDict] = VIOLATION_EXPLANATION_URLS.get(
            violation_code
        )
        if url_match is None:
            url_match = VIOLATION_EXPLANATION_URLS.get(prefix)
        if isinstance(url_match, str):
            return url_match
        elif isinstance(url_match, dict):
            hundredth_place = number[0]
            submatch = url_match.get(hundredth_place)
            if not submatch:
                for url_key, url_value in url_match.items():
                    if hundredth_place in url_key.split(','):
                        submatch = url_value
            if isinstance(submatch, str):
                return submatch
        if callable(url_match):
            url = url_match(code=violation_code)
        else:
            url = url_match
    return url or VIOLATION_DEFAULT_URL
