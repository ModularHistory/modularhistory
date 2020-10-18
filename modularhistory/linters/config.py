import argparse
import configparser
import fnmatch
import os
import re
import sys
from configparser import SectionProxy
from glob import glob
from typing import Any, Dict, Iterator, List, Optional, Pattern, Sequence, Set, Tuple, Union  # noqa: WPS235

from modularhistory.linters import utils

CONFIG_FILE = 'setup.cfg'

MultiOptions = Union[Sequence[str], str]

PatternList = List[Pattern]

PathPatternList = List[Pattern]

ErrorCodeSet = Set[str]

PerFileIgnore = Tuple[str, Set[str]]

ALL = None

GLOBAL_ONLY_OPTIONS = [
    'color',
    'show_ignored',
    'daemon',
    'exclude',
]

PER_MODULE_OPTIONS = [
    'select',
    'ignore',
    'warn',
    'include',
    'error_filters',
    'warning_filters',
]


class LinterOptions:
    """Options for linters."""

    # error codes:
    select: Optional[ErrorCodeSet] = None
    ignore: Optional[ErrorCodeSet] = None
    warn: Optional[ErrorCodeSet] = None

    # paths:
    include: Optional[PathPatternList] = None
    exclude: Optional[PathPatternList] = None

    # per-file ignores:
    per_file_ignores: Optional[List[PerFileIgnore]] = None

    # messages:
    error_filters: Optional[PatternList] = None
    warning_filters: Optional[PatternList] = None

    def __str__(self):
        """TODO: write docstring."""
        return f'{self.__dict__}'

    def is_excluded_path(self, path: str) -> bool:
        """TODO: write docstring."""
        return utils.match(self.exclude, path)

    def is_included_path(self, path: str) -> bool:
        """TODO: write docstring."""
        return utils.match(self.include, path)

    def error_is_ignored_in_file(self, filename: str, error_code: str):
        """Return True if an error is specifically ignored for the given filename."""
        for pattern, error_codes in self.per_file_ignores:
            if filename in glob(pattern) and error_code in error_codes:
                return True
        return False

    def get_message_level(self, message, error_code, filename) -> Optional[str]:
        """Returns a modified message level based on specified options."""
        error_is_ignored = any([
            utils.match(self.error_filters, message),
            self.ignore is ALL,
            error_code in self.ignore,
            self.error_is_ignored_in_file(filename=filename, error_code=error_code)
        ])
        # If error is to be ignored
        if error_is_ignored:
            return None
        # If we have specified something to check for
        elif self.select and error_code in self.select:
            return 'error'
        # If we have specified something to warn (ignore overrides this)
        elif self.warn is ALL or error_code in self.warn:
            return 'warning'
        # If checking everything
        elif self.select is ALL:
            return 'error'
        return None


# Options Handling

def _parse_multi_options(options: MultiOptions, split_token: str = ',') -> List[str]:  # noqa: S107
    """Split and strip and discard empties."""
    parsed_options: Sequence[str] = []
    if isinstance(options, str):
        options = options.strip()
        # Split the options by the specified split token, or by newlines
        if split_token in options:
            parsed_options = options.split(split_token)
        else:
            parsed_options = options.split('\n')
    else:
        parsed_options = options
    return [o.strip() for o in parsed_options if o.strip()]


def _glob_to_regex(s):
    """."""
    return re.compile(fnmatch.translate(s))


def _glob_list(s: MultiOptions) -> PathPatternList:
    """."""
    return [_glob_to_regex(x) for x in _parse_multi_options(s)]


def _per_file_ignores_list(s: MultiOptions) -> List[Tuple[str, Set[str]]]:
    per_file_ignores = []
    entries = _parse_multi_options(s, split_token='\n')  # noqa: S106
    for entry in entries:
        pattern, codes = entry.split(':')
        error_codes = {code.strip() for code in codes.split(',')}
        per_file_ignores.append((pattern.strip(), error_codes))
    return per_file_ignores


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


option_types = {
    'select': _error_set,
    'ignore': _error_set,
    'warn': _error_set,
    'args': _parse_multi_options,
    'include': _glob_list,
    'exclude': _glob_list,
    'per_file_ignores': _per_file_ignores_list,
    'error_filters': _regex_list,
    'warning_filters': _regex_list,
}


class ConfigFileOptionsParser:
    """TODO: add docstring."""

    def __init__(self, script_name: str):
        """
        Constructs the config file options parser.

        Sets script_name, which is used to determine which section of the config file to read.
        """
        self.script_name = script_name

    def apply(self, options: LinterOptions, module_options: List[Tuple[str, LinterOptions]]) -> None:
        """TODO: add docstring."""
        options_cls = options.__class__
        for updates, key in self.extract_updates(options):
            if updates:
                if key is None:
                    opt = options
                else:
                    opt = options_cls()
                    module_options.append((key, opt))
                for k, v in updates.items():
                    setattr(opt, k, v)

    def _parse_option(self, key: str, value: str, template: LinterOptions, section: SectionProxy) -> Any:
        option_type: Any = option_types.get(key)
        processed_value: Any
        if not option_type:
            dv = getattr(template, key, None)
            if dv is None:
                print(f'Unrecognized option: {key} = {value}', file=sys.stderr)
                return None
            option_type = type(dv)
        try:
            if option_type is bool:
                processed_value = section.getboolean(key)
            elif callable(option_type):
                processed_value = option_type(section.get(key))
            else:
                print(f'Cannot determine what type {key} should have', file=sys.stderr)
                return None
        except (ValueError, argparse.ArgumentTypeError) as err:
            print(f'{key}: {err}', file=sys.stderr)
            return None
        return processed_value

    def _parse_section(self, template: LinterOptions, section: SectionProxy) -> Dict[str, object]:
        results: Dict[str, object] = {}
        for key, value in section.items():
            processed_value = self._parse_option(key, value, template, section)
            if processed_value:
                results[key] = processed_value
        return results

    def extract_updates(self, options: LinterOptions) -> Iterator[Tuple[Dict[str, object], Optional[str]]]:
        """TODO: add docstring."""
        config_file = os.path.expanduser(CONFIG_FILE)
        parser = configparser.RawConfigParser()
        if not os.path.exists(config_file):
            raise EnvironmentError(f'No config file named {CONFIG_FILE} exists.')
        try:
            parser.read(config_file)
        except configparser.Error as err:
            print(f'{config_file}: {err}', file=sys.stderr)

        script_name = self.script_name
        if script_name in parser:
            section = parser[script_name]  # noqa: WPS529
            yield self._parse_section(options, section), None
        else:
            print(f'No [{self.script_name}] section in config file', file=sys.stderr)

        for name, section in parser.items():
            if name.startswith('mypyrun-'):
                prefix = f'{CONFIG_FILE}: [{name}]'
                updates = self._parse_section(options, section)

                if set(updates).intersection(GLOBAL_ONLY_OPTIONS):
                    print(
                        f'{prefix}: Per-module sections should only specify '
                        f'per-module flags ({", ".join(sorted(set(updates).intersection(GLOBAL_ONLY_OPTIONS)))})',
                        file=sys.stderr
                    )
                    updates = {k: v for k, v in updates.items() if k in PER_MODULE_OPTIONS}
                globs = name[8:]
                for file_glob in globs.split(','):
                    yield updates, file_glob
