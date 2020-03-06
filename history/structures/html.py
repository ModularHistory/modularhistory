from typing import Optional

# from sys import stderr
from bs4 import BeautifulSoup
from django.utils.safestring import SafeText, mark_safe
import re
from django.template.loader import render_to_string

image_key_regex = r'{{\ ?image:\ ?(.+?)\ ?}}'


class HTML:
    raw_html: str
    html: SafeText
    text: str

    def __init__(self, value: Optional[str]):
        if value:
            value = value.strip()
            if not value.startswith('<') and value.endswith('>'):
                value = f'<p>{value}</p>'
            self.raw_html = value
            html = self.raw_html
            if '{{' in html:
                from images.models import Image
                for match in re.finditer(image_key_regex, html):
                    key = match.group(1)
                    image = Image.objects.get(key=key)
                    image_html = render_to_string(
                        'images/_card.html',
                        context={'image': image, 'object': image}
                    )
                    if image.width < 300:
                        image_html = f'<div class="float-right pull-right">{image_html}</div>'
                    if image.width < 500:
                        image_html = f'<div style="text-align: center">{image_html}</div>'
                    html = html.replace(match.group(0), image_html)
            self.html = mark_safe(html)
            self.text = BeautifulSoup(self.raw_html, features='lxml').get_text()
        else:
            self.raw_html, self.html, self.text = '', mark_safe(''), ''

    # for Django Admin templates
    def __str__(self) -> str:
        # TODO: Add logic for converting back to unparsed Python vars so self.html can be used.
        # Don't directly use self.html here;
        # Python vars need to remain unparsed.
        return mark_safe(self.raw_html)

    # for BeautifulSoup
    def __len__(self):
        return len(self.raw_html)

    def __bool__(self):
        return bool(self.raw_html)


