from typing import List


def fix_comma_positions(string: str) -> str:
    """Rearrange commas to fit correctly inside double quotes."""
    return string.replace('",', ',"')


def components_to_string(components: List[str], delimiter=', '):
    """Combine a list of HTML components into an HTML string."""
    # Remove blank values
    components = [component for component in components if component]
    # Join components; rearrange commas and double quotes
    return fix_comma_positions(delimiter.join(components))


def truncate(string, max_length: int = 150):
    """Return a truncated version of the string."""
    string = string.strip().split('\n')[0]
    return f'{string[:max_length]} ...' if len(string) > max_length else string
