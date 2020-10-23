from typing import List, Optional

from bs4 import BeautifulSoup

from modularhistory.utils.string import components_to_string

NEW_TAB = '_blank'


def soupify(html_string: str) -> BeautifulSoup:
    """
    Wrap for the BeautifulSoup constructor.

    Specifies `lxml` as the parser.
    """
    return BeautifulSoup(html_string, features='lxml')


def compose_link(text, href, klass: Optional[str] = None, **html_attributes) -> str:
    """Build a link from the supplied text, href, klass, and html_attributes."""
    attributes = ' '.join(
        [
            f'{attr_name}="{attr_value}"'
            for attr_name, attr_value in html_attributes.items()
        ]
    )
    if klass:
        attributes = f'class="{klass}" {attributes}'
    return f'<a href="{href}" {attributes}>{text}</a>'


def components_to_html(components: List[str], delimiter=', ') -> str:
    """Combine a list of HTML components into an HTML string."""
    return components_to_string(components, delimiter=delimiter)
