"""
MyPy static typing check.

See https://docs.djangoproject.com/en/dev/topics/checks/.
"""

import os
import re
import sys
from collections import defaultdict
from typing import Optional, Pattern

from django.conf import settings
from mypy import api as mypy_client

from core.linters.config import CONFIG_FILE, PARSING_FAIL
from core.linters.config import ConfigFileOptionsParser as BaseConfigFileOptionsParser
from core.linters.config import LinterOptions, PerFileIgnore
from core.utils import linting

ERROR_CODE_LIST_URL: str = 'https://mypy.readthedocs.io/en/stable/error_code_list.html'

MYPY_SCRIPT_NAME: str = 'mypyrun'

os.environ['MYPY_DJANGO_CONFIG'] = f'./{CONFIG_FILE}'

MYPY_OUTPUT_PATTERN = re.compile(
    # Example --> history/checks.py:17: error: Need type annotation for 'errors'
    r'^(?P<location>.+\d+): (?P<level>\w+): (?P<message>.+)'
)

ALL = None

ERROR_CODE = re.compile(r'\[([a-z0-9\-_]+)\]$')

REVEALED_TYPE = 'Revealed type is'


class MyPyOptions(LinterOptions):
    """Options common to both the config file and the cli."""

    # error codes:
    select: Optional[set[str]] = None
    ignore: Optional[set[str]] = None
    warn: Optional[set[str]] = None

    # per-file ignores:
    per_file_ignores: Optional[list[PerFileIgnore]] = None

    # messages:
    error_filters: list[Pattern] = []
    warning_filters: list[Pattern] = []

    # global-only options:
    args: list[str] = []
    color: bool = True
    show_ignored: bool = False
    daemon: bool = False

    def __init__(self):
        """Construct MyPy options."""
        super().__init__()
        self.args = []


PerModuleOptions = list[tuple[str, MyPyOptions]]


def mypy(**kwargs):
    """Run mypy."""
    mypy_args = [settings.BASE_DIR, '--show-error-codes']
    output = mypy_client.run(mypy_args)[0]
    if output:
        process_mypy_output(output)


def process_mypy_output(output: str):
    """Process the output from mypy."""
    options, per_module_options = _get_mypy_options()
    matched_error = None  # used to know when to error a note related to an error
    errors_by_type: defaultdict[str, int] = defaultdict(int)
    errors: defaultdict[str, int] = defaultdict(int)
    warnings: defaultdict[str, int] = defaultdict(int)
    filtered: defaultdict[str, int] = defaultdict(int)

    for line in output.rstrip().split('\n'):
        parsed_line = _parse_output_line(line)
        if not parsed_line:
            print(line, end='')
            continue
        filename, line_number, level, message = parsed_line

        # Exclude errors from specific files
        if options.is_excluded_path(filename):
            filtered[filename] += 1
            continue

        # Use module options if applicable
        options = _get_module_options(options, per_module_options, filename)

        error_code = None
        match = ERROR_CODE.search(message)
        if match:
            error_code = match.group(1)
            message = message.replace(f'[{error_code}]', '').rstrip()

        level, error_code = _process_mypy_message(
            message, level, error_code, matched_error, filename, line_number, options
        )
        if level == 'error' and error_code:
            errors[filename] += 1
            errors_by_type[error_code] += 1
        elif level == 'warning':
            warnings[filename] += 1
        elif level == 'note':
            pass
    print()


def _process_mypy_message(
    message,
    level: str,
    error_code,
    matched_error,
    filename,
    line_number,
    options,
) -> tuple[str, str]:
    if level == 'error':
        # Change the level based on config
        level = options.get_message_level(message, error_code, filename)
        # Display the message
        if level or options.show_ignored:
            report(
                options,
                filename,
                line_number,
                level or 'error',
                message,
                not level,
                error_code,
            )
    elif level == 'note':
        if matched_error is not None:
            is_filtered = not matched_error[0]
            report(
                options,
                filename,
                line_number,
                level,
                message,
                is_filtered,
                matched_error[1],
            )
        elif message.startswith(REVEALED_TYPE):
            is_filtered = False
            report(options, filename, line_number, level, message, is_filtered)
    return level, error_code


def _get_mypy_options() -> tuple[MyPyOptions, PerModuleOptions]:
    """Return an Options object to be used by mypy."""
    options = MyPyOptions()
    module_options: PerModuleOptions = []
    ConfigFileOptionsParser().apply(options, module_options)  # type: ignore
    if options.select and options.ignore:
        overlap = options.select.intersection(options.ignore)
        if overlap:
            print(
                f'The same option must not be both selected and ignored: {", ".join(overlap)}',
                file=sys.stderr,
            )
            sys.exit(PARSING_FAIL)
    return options, module_options


def _get_module_options(
    options: MyPyOptions, per_module_options: PerModuleOptions, filename: str
) -> MyPyOptions:
    for _key, module_options in per_module_options:
        if module_options.is_included_path(filename):
            options = module_options
    return options


def _parse_output_line(line: str) -> Optional[tuple[str, ...]]:
    """Parse a line of output from mypy."""
    parsed_line = MYPY_OUTPUT_PATTERN.match(line)
    if not parsed_line:
        return None
    location = parsed_line.group('location')
    level = parsed_line.group('level')
    message = parsed_line.group('message')
    filename, line_number = location.split(':')
    return filename, line_number, level, message


def report(
    options: MyPyOptions,
    filename: str,
    line_number: str,
    status: str,
    msg: str,
    is_filtered: bool,
    error_key: Optional[str] = None,
):
    """Report an error to stdout."""
    display_attrs = ['dark'] if options.show_ignored and is_filtered else None
    filename = linting.colored(filename, 'cyan', attrs=display_attrs)
    line_number = linting.colored(f'{line_number}', attrs=display_attrs)
    color = linting.COLORS[status]
    status = linting.colored(f'{status}', color, attrs=display_attrs)
    msg = linting.colored(msg, color, attrs=display_attrs)
    if 'found module but no type hints or library stubs' not in msg:  # TODO
        print(
            f'{"IGNORED: " if options.show_ignored and is_filtered else ""}'
            f'{filename}:{line_number}: {msg}  [{error_key}: {ERROR_CODE_LIST_URL}]'
        )


class ConfigFileOptionsParser(BaseConfigFileOptionsParser):
    """Config file options parser for mypy."""

    def __init__(self, script_name: str = MYPY_SCRIPT_NAME):
        """Construct the mypy options parser."""
        super().__init__(script_name=script_name)
