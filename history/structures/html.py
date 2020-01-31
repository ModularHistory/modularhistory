from typing import Optional

# from sys import stderr
from bs4 import BeautifulSoup
from django.db.models.fields.files import FieldFile
from django.utils.safestring import SafeText, mark_safe


class HTML:
    raw_html: str
    html: SafeText
    text: str

    def __init__(self, value: Optional[str]):
        if value:
            self.raw_html = value
            self.html = mark_safe(self.raw_html)
            self.text = BeautifulSoup(self.raw_html, features="lxml").get_text()
        else:
            self.raw_html, self.html, self.text = '', mark_safe(''), ''

    # for Django Admin templates
    def __str__(self) -> str:
        return self.html

    # for BeautifulSoup
    def __len__(self):
        return len(self.raw_html)

    def __bool__(self):
        return bool(self.raw_html)


