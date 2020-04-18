import re
from typing import Callable, Optional, Union

from django.template.loader import render_to_string
from django.utils.safestring import SafeText
from tinymce.models import HTMLField as MceHTMLField
from django.core.exceptions import ObjectDoesNotExist
from history.structures.html import HTML

image_key_regex = r'{{\ ?image:\ ?(.+?)\ ?}}'
citation_key_regex = r'{{\ ?citation:\ ?(.+?)\ ?}}'
source_key_regex = r'{{\ ?source:\ ?(.+?)\ ?}}'


def process(_, html: str) -> str:
    if '{{' in html:
        from images.models import Image
        from sources.models import Source, Citation
        # Process images
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
        # Process citations
        for match in re.finditer(citation_key_regex, html):
            try:
                key = match.group(1)
                print(f'Found match: {match.group(0)}')
                try:
                    citation = Citation.objects.get(pk=key)
                    citation_html = (f'<a href="#{citation.html_id}" title="{citation}">'
                                     f'<sup>{citation.number}</sup>'
                                     f'</a>')
                except ObjectDoesNotExist:
                    citation_html = f'[UNABLE TO RETRIEVE CITATION: {key}]'
                html = html.replace(match.group(0), citation_html)
            except Exception as e:
                print(f'Could not process citation in HTML; encountered exception: {e}')
        # Process sources
        for match in re.finditer(source_key_regex, html):
            key = match.group(1)
            source = Source.objects.get(pk=key)
            source_html = f'{source.html}'
            html = html.replace(match.group(0), source_html)
    return html


class HTMLField(MceHTMLField):
    """A string field for HTML content; uses the TinyMCE widget in forms."""
    raw_value: str
    html: SafeText
    text: str
    DEFAULT_PROCESSOR: Callable = process
    processor: Optional[Callable] = DEFAULT_PROCESSOR

    # def __init__(self, *args, **kwargs):
    #     # if 'processor' in kwargs and kwargs['processor'] != self.DEFAULT_PROCESSOR:
    #     #     self.processor = kwargs['processor']
    #     print()
    #     print(f'args: {args}')
    #     print(f'kwargs: {kwargs}')
    #     # if 'verbose_name' in kwargs:
    #     #     print(f'ERROR: verbose_name of `{kwargs.get("verbose_name")}` is present in kwargs; removing ...')
    #     #     kwargs.pop('verbose_name')
    #     super().__init__(self, *args, **kwargs)
    #     print('success\n')

    def clean(self, value, model_instance) -> HTML:
        html = super().clean(value=value, model_instance=model_instance)
        raw_html = html.raw_value.replace(
            '<blockquote>', '<blockquote class="blockquote">'
        ).replace(
            '<table>', '<table class="table">'
        ).strip()
        # Remove empty divs
        raw_html = re.sub(r'\n?<div[^>]+?>&nbsp;<\/div>', '', raw_html)
        raw_html = re.sub(r'<div id=\"i4c-draggable-container\"[^\/]+</div>', '', raw_html)
        raw_html = re.sub(r'<p>&nbsp;<\/p>', '', raw_html)
        if not raw_html.startswith('<') and raw_html.endswith('>'):
            raw_html = f'<p>{raw_html}</p>'
        html.raw_value = raw_html
        return html

    # def deconstruct(self):
    #     field_class = 'history.fields.HTMLField'
    #     name, path, args, kwargs = super().deconstruct()
    #     if self.processor != self.DEFAULT_PROCESSOR:
    #         kwargs['processor'] = self.processor
    #     return name, field_class, args, kwargs

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def from_db_value(self, value: Optional[str], expression, connection) -> Optional[HTML]:
        if value is None:
            return value
        if not value.startswith('<') and value.endswith('>'):
            value = f'<p>{value}</p>'
        # Remove empty divs
        value = re.sub(r'\n?<div[^>]+?>&nbsp;<\/div>', '', value)
        value = re.sub(r'<div id=\"i4c-draggable-container\"[^\/]+</div>', '', value)
        value = re.sub(r'<p>&nbsp;<\/p>', '', value)
        html = value
        if self.processor:
            try:
                html = self.processor(html)
            except RecursionError as e:
                print(f'Unable to process HTML; encountered exception: {e}')
        return HTML(value, processed_value=html)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(self, value: Optional[Union[HTML, str]]) -> Optional[HTML]:
        if isinstance(value, HTML):
            return value
        elif not value:
            return None
        return HTML(value)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-python-objects-to-query-values
    def get_prep_value(self, value: Optional[HTML]) -> Optional[str]:
        if isinstance(value, HTML):
            return value.raw_value
        elif not value:
            return None

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-query-values-to-database-values
    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#id2
    def value_to_string(self, obj) -> str:
        value = self.value_from_object(obj)
        return self.get_prep_value(value) or ''
