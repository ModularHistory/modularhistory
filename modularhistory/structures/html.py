import logging
from typing import Callable, Optional

from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from modularhistory.utils.html import soupify
from modularhistory.utils.string import truncate


class HTML:
    """HTML with a raw value, optional processor, and text."""

    raw_value: str
    processor: Optional[Callable]

    def __init__(self, raw_value: Optional[str], processor: Optional[Callable] = None):
        """Construct an HTML object."""
        self.processor = processor
        if raw_value:
            raw_value = raw_value.strip()
            self.raw_value = raw_value
            self._html = None  # Defer to the `html` property
        else:
            self.raw_value = ''
            self._html = format_html('')

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

    @property
    def html(self) -> SafeString:
        """Return the processed HTML value."""
        processed_html = ''
        if self._html is not None:
            return self._html
        else:
            if callable(self.processor):
                try:
                    processed_html = self.processor(self.raw_value)
                    logging.debug(f'Processed HTML: {truncate(processed_html)}')
                except (RecursionError, Exception) as error:
                    logging.error(
                        f'ERROR: {error} resulted from attempting to process HTML:\n'
                        f'{truncate(self.raw_value)}\n'
                    )
        html = processed_html or self.raw_value
        try:
            self._html = format_html(html)
        except ValueError as e:
            logging.error(f'>>> {e}: {html}')
            self._html = mark_safe(html)
        return self._html

    @property
    def text(self) -> str:
        """Return the textual content with all HTML tags removed."""
        return soupify(self.raw_value).get_text() if self.raw_value else ''
