from typing import Optional, Sequence


def fix_comma_positions(string: str) -> str:
    """Rearrange commas to fit correctly inside double quotes."""
    return string.replace('",', ',"')


def components_to_string(components: Sequence[Optional[str]], delimiter: str = ', '):
    """Combine a sequence of HTML components into an HTML string."""
    # Remove blank values
    components = [component for component in components if component]
    # Join components; rearrange commas and double quotes
    return fix_comma_positions(delimiter.join(components))


def truncate(string, max_length: int = 150, strip_newlines: bool = True):
    """Return a truncated version of the string."""
    if strip_newlines:
        string = string.replace('\n', ' ')
    string = string.strip()
    return f'{string[:max_length]} ...' if len(string) > max_length else string


def dedupe_newlines(string: str):
    """Return the string with unnecessary newlines removed."""
    return ''.join([s for s in string.strip().splitlines(True) if s.strip()])
