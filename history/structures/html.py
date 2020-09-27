from typing import Optional

from bs4 import BeautifulSoup
from django.utils.html import SafeString, format_html


class HTML:
    """TODO: add docstring."""

    raw_value: str
    html: SafeString
    text: str

    def __init__(self, raw_value: Optional[str], processed_value: Optional[str] = None):
        """TODO: add docstring."""
        if raw_value:
            raw_value = raw_value.strip()
            self.raw_value = raw_value
            self.html = format_html(processed_value or raw_value)
            self.text = BeautifulSoup(self.raw_value, features='lxml').get_text()
        else:
            self.raw_value = ''
            self.html = format_html('')
            self.text = ''

    # for Django Admin templates
    def __str__(self) -> str:
        """TODO: write docstring."""
        # TODO: Add logic for converting back to unparsed Python vars so self.html can be used.
        # Don't directly use self.html here;
        # Python vars need to remain unparsed.
        return format_html(self.raw_value)

    # for BeautifulSoup
    def __len__(self):
        """TODO: add docstring."""
        return len(self.raw_value)

    def __bool__(self):
        """TODO: add docstring."""
        return bool(self.raw_value)
