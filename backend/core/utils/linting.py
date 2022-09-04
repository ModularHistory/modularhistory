"""
Utils for checks.

https://docs.djangoproject.com/en/dev/topics/checks/
"""

from typing import Pattern

COLORS = {
    'error': 'red',
    'warning': 'yellow',
    'note': None,
}
TERM_ATTRIBUTES = {
    'bold': 1,
    'dark': 2,
    'underline': 4,
    'blink': 5,
    'reverse': 7,
    'concealed': 8,
}
TERM_COLORS = {
    'grey': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
}
TERM_RESET = '\033[0m'


def colored(text, color=None, attrs=None):
    """TODO: add docstring."""
    esc = '\033[%dm%s'
    if color is not None:
        text = esc % (TERM_COLORS[color], text)
    if attrs is not None:
        for attr in attrs:
            text = esc % (TERM_ATTRIBUTES[attr], text)
    text += TERM_RESET
    return text


def match(regex_list: list[Pattern], string: str) -> bool:
    """Return whether the string matches any of the patterns in the regex list."""
    for regex in regex_list:
        if regex.search(string):
            return True
    return False


# The check framework is used for multiple different kinds of checks. As such, errors
# and warnings can originate from models or other django objects. The `CheckMessage`
# requires an obj as the source of the message and so we create a temporary obj
# that simply displays the file and line number associated with the message (i.e. "location")
class ErrorLocation:
    """TODO: add docstring."""

    def __init__(self, location):
        """TODO: add docstring."""
        self.location = location

    def __str__(self) -> str:
        """TODO: write docstring."""
        return self.location
