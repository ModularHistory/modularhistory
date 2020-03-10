from typing import Optional

from bs4 import BeautifulSoup
from django.utils.safestring import SafeText, mark_safe


class HTML:
    raw_value: str
    html: SafeText
    text: str

    def __init__(self, raw_value: Optional[str], processed_value: Optional[str] = None):
        if raw_value:
            raw_value = raw_value.strip()
            html = processed_value or raw_value
            self.raw_value = raw_value
            self.html = mark_safe(html)
            self.text = BeautifulSoup(self.raw_value, features='lxml').get_text()
        else:
            self.raw_value, self.html, self.text = '', mark_safe(''), ''

    # for Django Admin templates
    def __str__(self) -> str:
        # TODO: Add logic for converting back to unparsed Python vars so self.html can be used.
        # Don't directly use self.html here;
        # Python vars need to remain unparsed.
        return mark_safe(self.raw_value)

    # for BeautifulSoup
    def __len__(self):
        return len(self.raw_value)

    def __bool__(self):
        return bool(self.raw_value)


