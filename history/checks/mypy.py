"""https://docs.djangoproject.com/en/3.1/topics/checks/"""

import argparse
import configparser
import fnmatch
import json
import os
import re
# from os import path
import sys
from collections import defaultdict
from typing import Any, List, Optional, Set, Sequence, Dict, Tuple, Union, DefaultDict, Pattern, Iterator

# from django.core.checks.messages import CheckMessage, DEBUG, INFO, WARNING, ERROR
from django.conf import settings
from django.core.checks import register
from mypy import api as mypy_client

from history.checks import utils

MultiOptions = Union[Sequence[str], str]

MYPY_SCRIPT_NAME: str = 'mypyrun'
CONFIG_FILE = 'setup.cfg'
CONFIG_FILES = (CONFIG_FILE,)

# Example:
# history/checks.py:17: error: Need type annotation for 'errors'
MYPY_OUTPUT_PATTERN = re.compile(r'^(.+\d+): (\w+): (.+)')

ALL = None

# choose an exit that does not conflict with mypy's
PARSING_FAIL = 100
ERROR_CODE = re.compile(r'\[([a-z0-9\-_]+)\]$')

REVEALED_TYPE = 'Revealed type is'

GLOBAL_ONLY_OPTIONS = [
    'color',
    'show_ignored',
    'daemon',
    'exclude',
    'mypy_executable',
]


class Options:
    """Options common to both the config file and the cli."""
    PER_MODULE_OPTIONS = [
        'select',
        'ignore',
        'warn',
        'include',
        'error_filters',
        'warning_filters',
    ]
    # error codes:
    select: Optional[Set[str]] = None
    ignore: Optional[Set[str]] = None
    warn: Optional[Set[str]] = None
    # paths:
    include: List[Pattern] = None
    exclude: List[Pattern] = None
    # messages:
    error_filters: List[Pattern] = None
    warning_filters: List[Pattern] = None

    # global-only options:
    args: List[str] = None
    color: bool = True
    show_ignored: bool = False
    daemon: bool = False
    mypy_executable: Optional[str] = None

    def __str__(self):
        return f'{self.__dict__}'

    def __init__(self):
        self.select = ALL
        self.ignore = set()
        self.warn = set()
        self.include = []
        self.exclude = []
        self.error_filters = []
        self.warning_filters = []
        self.args = []

    def is_excluded_path(self, path: str) -> bool:
        """TODO: write docstring."""
        return utils.match(self.exclude, path)

    def is_included_path(self, path: str) -> bool:
        """TODO: write docstring."""
        return utils.match(self.include, path)


@register()
def mypy(app_configs: Optional[List], **kwargs) -> List:
    """."""
    # print('Performing mypy checks...\n')
    # print(f'app_configs: {app_configs}')
    # print(f'kwargs: {kwargs}')
    options = Options()
    module_options: List[Tuple[str, Options]] = []
    parsers = [
        ConfigFileOptionsParser(),
        JsonEnvVarOptionsParser(),
    ]
    for p in parsers:
        p.apply(options, module_options)
    if options.select and options.ignore:
        overlap = options.select.intersection(options.ignore)
        if overlap:
            print(f'The same option must not be both selected and ignored: {", ".join(overlap)}',
                  file=sys.stderr)
            sys.exit(PARSING_FAIL)

    # By default, run mypy against the whole database everytime checks are performed.
    # If performance is an issue then `app_configs` can be inspected and the scope
    # of the mypy check can be restricted
    mypy_args = [
        settings.BASE_DIR,
        '--show-error-codes'
    ]
    results = mypy_client.run(mypy_args)
    output = results[0]
    if not output:
        return []

    # used to know when to error a note related to an error
    matched_error = None

    errors_by_type: DefaultDict[str, int] = defaultdict(int)
    errors: DefaultDict[str, int] = defaultdict(int)
    warnings: DefaultDict[str, int] = defaultdict(int)
    filtered: DefaultDict[str, int] = defaultdict(int)

    messages: List = []

    for line in output.rstrip().split('\n'):
        parsed_line = MYPY_OUTPUT_PATTERN.match(line)
        if not parsed_line:
            print(line, end='')
            continue
        location = parsed_line.group(1)
        level = parsed_line.group(2)
        message = parsed_line.group(3)
        filename, line_number = location.split(':')

        # Exclude errors from specific files
        if options.is_excluded_path(filename):
            print(f'Excluding {filename}...')
            filtered[filename] += 1
            continue

        # Use module options if applicable
        for key, _options in module_options:
            if _options.is_included_path(filename):
                options = _options

        error_code = None
        m = ERROR_CODE.search(message)
        if m:
            error_code = m.group(1)
            message = message.replace(f'[{error_code}]', '').rstrip()

        # Change the level based on config
        if level == 'error':
            # If we have specified something to check for
            if options.select is not ALL and error_code in options.select:
                level = 'error' if not utils.match(options.error_filters, message) else None
            # If we have specified something to ignore (specific selects override this)
            elif options.ignore is ALL or error_code in options.ignore:
                level = None
            # If we have specified something to warn (ignore overrides this)
            elif options.warn is ALL or error_code in options.warn:
                level = 'warning' if not utils.match(options.warning_filters, message) else None
            # If checking everything
            elif options.select is ALL:
                level = 'error' if not utils.match(options.error_filters, message) else None
            else:
                level = None

            # Include the message in aggregates
            if level == 'error':
                errors[filename] += 1
                errors_by_type[error_code] += 1
            elif level == 'warning':
                warnings[filename] += 1
            elif level is None:
                filtered[filename] += 1

            # Display the message
            if level or options.show_ignored:
                report(options, filename, line_number, level or 'error', message, not level, error_code)
                matched_error = level, error_code
            else:
                matched_error = None
        elif level == 'note' and matched_error is not None:
            report(options, filename, line_number, level, message, not matched_error[0], matched_error[1])
        elif level == 'note' and message.startswith(REVEALED_TYPE):
            report(options, filename, line_number, level, message, False)

        # message_level = DEBUG
        # if level == 'note':
        #     message_level = INFO
        # elif level == 'warning':
        #     message_level = WARNING
        # elif level == 'error':
        #     message_level = ERROR
        # else:
        #     print(f'Unrecognized mypy level: {level}')
        # message_level = WARNING
        # messages.append(CheckMessage(message_level, message, obj=MyPyErrorLocation(location)))

    # def print_stat(key, value):
    #     print("{:.<50}{:.>8}".format(key, value))
    #
    # error_files = set(errors.keys())
    # warning_files = set(warnings.keys())
    # filtered_files = set(filtered.keys())
    #
    # print()
    # print_stat("Errors", sum(errors.values()))
    # print_stat("Warnings", sum(warnings.values()))
    # print_stat("Filtered", sum(filtered.values()))
    # print()
    # for (code, count) in sorted(errors_by_type.items(), key=lambda v: v[1],
    #                             reverse=True):
    #     print_stat(code, count)
    # print()
    # print_stat("Files with errors or warnings (excluding filtered)",
    #            len(error_files | warning_files))
    # print_stat("Files with errors or warnings (including filtered)",
    #            len(error_files | warning_files | filtered_files))
    print()
    return messages


def report(options: Options, filename: str, line_number: str, status: str, msg: str, is_filtered: bool,
           error_key: Optional[str] = None) -> None:
    """Report an error to stdout."""
    display_attrs = ['dark'] if options.show_ignored and is_filtered else None
    filename = utils.colored(filename, 'cyan', attrs=display_attrs)
    line_number = utils.colored(f'{line_number}', attrs=display_attrs)
    color = utils.COLORS[status]
    status = utils.colored(f'{status}', color, attrs=display_attrs)
    msg = utils.colored(msg, color, attrs=display_attrs)
    print(f'{"IGNORED: " if options.show_ignored and is_filtered else ""}'
          f'{filename}:{line_number}: {status}: {msg}  [{error_key}]')


# Options Handling

def _parse_multi_options(options: MultiOptions, split_token: str = ',') -> List[str]:
    """Split and strip and discard empties."""
    if isinstance(options, str):
        options = options.split(split_token)
    return [o.strip() for o in options if o.strip()]


def _glob_to_regex(s):
    """."""
    return re.compile(fnmatch.translate(s))


def _glob_list(s: MultiOptions) -> List[Pattern]:
    """."""
    return [_glob_to_regex(x) for x in _parse_multi_options(s)]


def _regex_list(s: MultiOptions) -> List[Pattern]:
    """."""
    return [re.compile(x) for x in _parse_multi_options(s)]


def _error_set(s: MultiOptions) -> Optional[Set[str]]:
    """."""
    result = set()
    for res in _parse_multi_options(s):
        if res == '*':
            return None
        else:
            result.add(res)
    return result


config_types = {
    'select': _error_set,
    'ignore': _error_set,
    'warn': _error_set,
    'args':  _parse_multi_options,
    'include': _glob_list,
    'exclude': _glob_list,
    'error_filters': _regex_list,
    'warning_filters': _regex_list,
}


class BaseOptionsParser:
    """."""

    def extract_updates(self, options: Options) -> Iterator[Tuple[Dict[str, object], Optional[str]]]:
        """."""
        raise NotImplementedError

    def apply(self, options: Options, module_options: List[Tuple[str, Options]]) -> None:
        """."""
        for updates, key in self.extract_updates(options):
            if updates:
                if key is None:
                    opt = options
                else:
                    opt = Options()
                    module_options.append((key, opt))
                for k, v in updates.items():
                    setattr(opt, k, v)


class ConfigFileOptionsParser(BaseOptionsParser):
    """."""

    def __init__(self, filename=None):
        self.filename = filename

    def _parse_section(self, prefix: str, template: Options, section: configparser.SectionProxy) -> Dict[str, object]:
        """."""
        results: Dict[str, object] = {}
        for key in section:
            ct: Any
            if key in config_types:
                ct = config_types[key]
            else:
                dv = getattr(template, key, None)
                if dv is None:
                    print(f'{prefix}: Unrecognized option: {key} = {section[key]}',
                          file=sys.stderr)
                    continue
                ct = type(dv)
            v: Any
            try:
                if ct is bool:
                    v = section.getboolean(key)
                elif callable(ct):
                    try:
                        v = ct(section.get(key))
                    except argparse.ArgumentTypeError as err:
                        print(f'{prefix}: {key}: {err}', file=sys.stderr)
                        continue
                else:
                    print(f'{prefix}: Cannot determine what type {key} should have', file=sys.stderr)
                    continue
            except ValueError as err:
                print(f'{prefix}: {key}: {err}', file=sys.stderr)
                continue
            results[key] = v
        return results

    def extract_updates(self, options: Options) -> Iterator[Tuple[Dict[str, object], Optional[str]]]:
        """."""
        if self.filename is not None:
            config_files: Tuple[str, ...] = (self.filename,)
        else:
            config_files = tuple(map(os.path.expanduser, CONFIG_FILES))
        parser = configparser.RawConfigParser()
        for config_file in config_files:
            if not os.path.exists(config_file):
                continue
            try:
                parser.read(config_file)
            except configparser.Error as err:
                print(f'{config_file}: {err}', file=sys.stderr)
            else:
                file_read = config_file
                # options.config_file = file_read
                break
        else:
            print('No config files found')
            return

        if MYPY_SCRIPT_NAME not in parser:
            if self.filename or file_read not in CONFIG_FILES:
                print(f'{file_read}: No [mypyrun] section in config file', file=sys.stderr)
        else:
            section = parser[MYPY_SCRIPT_NAME]

            prefix = f'{file_read}: [mypy]'
            yield self._parse_section(prefix, options, section), None

        for name, section in parser.items():
            if name.startswith('mypyrun-'):
                prefix = f'{file_read}: [{name}]'
                updates = self._parse_section(prefix, options, section)

                if set(updates).intersection(GLOBAL_ONLY_OPTIONS):
                    print(f'{prefix}: Per-module sections should only specify '
                          f'per-module flags ({", ".join(sorted(set(updates).intersection(GLOBAL_ONLY_OPTIONS)))})',
                          file=sys.stderr)
                    updates = {k: v for k, v in updates.items() if k in Options.PER_MODULE_OPTIONS}
                globs = name[8:]
                for glob in globs.split(','):
                    yield updates, glob


class JsonOptionsParser(BaseOptionsParser):
    """."""

    def __init__(self, json_data):
        self.json_data = json_data

    def extract_updates(self, options: Options) -> Iterator[Tuple[Dict[str, object], Optional[str]]]:
        """."""
        if self.json_data:
            results: Dict[str, object] = {}
            for key, v in self.json_data.items():
                if key in config_types:
                    ct = config_types[key]
                    v = ct(v)
                else:
                    dv = getattr(options, key, None)
                    if dv is None:
                        print(f'Unrecognized option: {key} = {v}', file=sys.stderr)
                        continue
                results[key] = v
            yield results, None


class JsonEnvVarOptionsParser(JsonOptionsParser):
    """."""

    def __init__(self):
        opts = os.environ.get('MYPYRUN_OPTIONS')
        json_data = json.loads(opts) if opts else None
        super(JsonEnvVarOptionsParser, self).__init__(json_data)
