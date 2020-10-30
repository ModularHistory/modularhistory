from typing import Optional

from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
import logging
from modularhistory.utils.html import soupify
from modularhistory.utils.string import truncate


class HTML:
    """HTML with a raw value, optional processed value, and text."""

    raw_value: str
    html: SafeString
    text: str

    def __init__(self, raw_value: Optional[str], processed_value: Optional[str] = None):
        """Construct an HTML object."""
        if raw_value:
            raw_value = raw_value.strip()
            processed_value = processed_value or raw_value
            self.raw_value = raw_value
            try:
                self.html = format_html(processed_value)
            except ValueError as e:
                logging.error(f'>>> {e}: {processed_value}')
                self.html = mark_safe(processed_value)
            self.text = soupify(self.raw_value).get_text()
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
        try:
            return format_html(self.raw_value)
        except ValueError as e:
            logging.error(f'>>> {e}: {truncate(self.raw_value)}')
            return mark_safe(self.raw_value)

    # for BeautifulSoup
    def __len__(self):
        """Return the number of characters in the HTML."""
        return len(self.raw_value)

    def __bool__(self):
        """Return whether the HTML has a non-empty value."""
        return bool(self.raw_value)
