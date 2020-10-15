from typing import Optional

from bs4 import BeautifulSoup
from django.utils.html import format_html
from django.utils.safestring import SafeString


class HTML:
    """TODO: add docstring."""

    raw_value: str
    html: SafeString
    text: str

    def __init__(self, raw_value: Optional[str], processed_value: Optional[str] = None):
        """TODO: add docstring."""
        if raw_value:
            raw_value = raw_value.strip()
            processed_value = processed_value or raw_value
            self.raw_value = raw_value
            self.html = format_html(processed_value)
            self.text = BeautifulSoup(self.raw_value, features='lxml').get_text()
        else:
            self.raw_value = ''
            self.html = format_html('')
            self.text = ''

    # for Django Admin templates
    def __str__(self) -> SafeString:
        """
        Return the string representation of the HTML object.

        This value is displayed (and modified) in the Django admin site.
        """
        # TODO: Add logic for converting back to unparsed Python vars so self.html can be used.
        # Do not directly use self.html here; Python vars need to remain unparsed.
        return format_html(self.raw_value)

    # for BeautifulSoup
    def __len__(self):
        """TODO: add docstring."""
        return len(self.raw_value)

    def __bool__(self):
        """TODO: add docstring."""
        return bool(self.raw_value)
