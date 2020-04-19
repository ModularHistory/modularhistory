import re
from sys import stderr
from typing import Callable, Optional, Union
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.safestring import SafeText
from tinymce.models import HTMLField as MceHTMLField

from history.structures.html import HTML

image_key_regex = r'{{\ ?image:\ ?(.+?)\ ?}}'
citation_key_regex = r'\ ?{{\ ?citation:\ ?(.+?)\ ?}}'
source_key_regex = r'{{\ ?source:\ ?(.+?)\ ?}}'
entity_name_regex = r'<span class=\"entity-name\" data-entity-id=\"(\d+)\">(.+?)</span>'


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
            key = match.group(1)
            print(f'Found match: {match.group(0)}')
            try:
                citation = Citation.objects.get(pk=key)
            except ObjectDoesNotExist:
                print(f'UNABLE TO RETRIEVE CITATION: {key}', file=stderr)
                continue
            html_id = citation.html_id
            citation_html = (f'<a href="#{html_id}" title="{citation}">'
                             f'<sup>{citation.number}</sup>'
                             f'</a>')
            html = html.replace(match.group(0), citation_html)
        # Process sources
        for match in re.finditer(source_key_regex, html):
            key = match.group(1)
            source = Source.objects.get(pk=key)
            source_html = f'{source.html}'
            html = html.replace(match.group(0), source_html)
    if re.search(entity_name_regex, html):
        from entities.models import Entity
        processed_entity_keys = []
        for match in re.finditer(entity_name_regex, html):
            key = match.group(1)
            entity_name = match.group(2)
            # Process the entity name if it hasn't already been processed
            if key not in processed_entity_keys:
                processed_entity_keys.append(key)
                try:
                    # entity = Entity.objects.get(pk=key)
                    entity_link = (f'<a href="{reverse("entities:detail", args=key)}" '
                                   f'target="_blank">{entity_name}</a>')
                    html = html.replace(match.group(0), entity_link)
                except Exception as e:
                    print(f'{e}', file=stderr)
    return html


class HTMLField(MceHTMLField):
    """A string field for HTML content; uses the TinyMCE widget in forms."""
    raw_value: str
    html: SafeText
    text: str
    DEFAULT_PROCESSOR: Callable = process
    processor: Optional[Callable] = DEFAULT_PROCESSOR

    def __init__(self, *args, **kwargs):
        if 'processor' in kwargs and kwargs['processor'] != self.DEFAULT_PROCESSOR:
            self.processor = kwargs['processor']
        super().__init__(*args, **kwargs)

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
        if hasattr(model_instance, 'attributees') or hasattr(model_instance, 'involved_entities'):
            entities = (getattr(model_instance, 'attributees', None)
                        or getattr(model_instance, 'involved_entities', None))
            if entities and entities.exists():
                entities = entities.all()
                from entities.models import Entity
                for e in entities:
                    entity: Entity = e
                    for name in set([entity.name] + entity.aliases):
                        raw_html = re.sub(
                            rf'(^|[^>])({name})([^\w])',
                            rf'\g<1><span class="entity-name" data-entity-id="{entity.pk}">\g<2></span>\g<3>',
                            raw_html
                        )
                    print(f'>>> {entity}', file=stderr)
        if not raw_html.startswith('<') and raw_html.endswith('>'):
            raw_html = f'<p>{raw_html}</p>'
        html.raw_value = raw_html
        return html

    def deconstruct(self):
        field_class = 'history.fields.HTMLField'
        name, path, args, kwargs = super().deconstruct()
        if self.processor != self.DEFAULT_PROCESSOR:
            kwargs['processor'] = self.processor
        return name, field_class, args, kwargs

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
                print(f'Unable to process HTML; encountered exception: {e}', file=stderr)
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
