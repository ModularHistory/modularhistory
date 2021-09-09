from typing import Optional, Sequence

import scrubadub
from textblob import download_corpora
from textblob.exceptions import MissingCorpusError


def fix_comma_positions(string: str) -> str:
    """Rearrange commas to fit correctly inside double quotes."""
    return string.replace('",', ',"')


def components_to_string(components: Sequence[Optional[str]], delimiter: str = ', '):
    """Combine a sequence of HTML components into an HTML string."""
    # Remove blank values
    real_components: list[str] = [component for component in components if component]
    # Join components; rearrange commas and double quotes
    return fix_comma_positions(delimiter.join(real_components))


def redact(string) -> str:
    """Redact the string, replacing any PII."""
    try:
        return scrubadub.clean(string, replace_with='identifier')
    except MissingCorpusError:
        download_corpora.main()
        return scrubadub.clean(string, replace_with='identifier')


def truncate(string, max_length: int = 150, strip_newlines: bool = True):
    """Return a truncated version of the string."""
    if strip_newlines:
        string = string.replace('\n', ' ')
    string = string.strip()
    return f'{string[:max_length]} ...' if len(string) > max_length else string


def dedupe_newlines(string: str):
    """Return the string with unnecessary newlines removed."""
    return ''.join([s for s in string.strip().splitlines(True) if s.strip()])
