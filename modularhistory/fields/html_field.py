import re
from sys import stderr
from typing import Callable, Iterable, Optional, TYPE_CHECKING, Type, Union

from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString
from tinymce.models import HTMLField as MceHTMLField

from modularhistory.constants import MODEL_CLASS_PATHS
from modularhistory.structures.html import HTML

if TYPE_CHECKING:
    from modularhistory.models import Model

# group 1: entity pk
# group 2: entity name
ENTITY_NAME_REGEX = r'<span class=\"entity-name\" data-entity-id=\"(\d+)\">(.+?)</span>'

# group 1: obj type
OBJECT_REGEX = re.compile(r'<< ?(\w+):(?!>>)[\s\S]+? ?>>')


def process(_, html: str, processable_content_types: Iterable[str]) -> str:
    """TODO: add docstring."""
    for match in OBJECT_REGEX.finditer(html):
        placeholder = match.group(0)
        object_type = match.group(1)
        model_cls_str = MODEL_CLASS_PATHS.get(object_type)
        if model_cls_str:
            model_cls: Type[Model] = import_string(model_cls_str)
            # TODO
            object_match = model_cls.admin_placeholder_regex.match(placeholder)
            object_html = model_cls.get_object_html(object_match, use_preretrieved_html=True)
            html = html.replace(placeholder, object_html)
        else:
            print(f'Unable to retrieve model class string for `{object_type}`', file=stderr)
    return html


class HTMLField(MceHTMLField):
    """A string field for HTML content; uses the TinyMCE widget in forms."""

    raw_value: str
    html: SafeString
    text: str
    default_processor: Callable = process
    processor: Optional[Callable] = default_processor

    # Types of processable objects included in HTML
    processable_content_types: Iterable[str] = ['quote', 'image', 'citation', 'source']

    def __init__(self, *args, **kwargs):
        """Constructs an HTML field instance."""
        if 'processor' in kwargs and kwargs['processor'] != self.default_processor:
            self.processor = kwargs['processor']
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance: 'Model') -> HTML:
        """Returns a cleaned, ready-to-save instance of HTML."""
        html = super().clean(value=value, model_instance=model_instance)
        raw_html = html.raw_value
        replacements = (
            (r'<blockquote>', '<blockquote class="blockquote">'),
            (r'<table>', '<table class="table">'),
            # Remove empty divs
            (r'\n?<div[^>]+?>&nbsp;<\/div>', ''),
            (r'<div id=\"i4c-draggable-container\"[^\/]+</div>', ''),
            (r'<p>&nbsp;<\/p>', '')
        )
        for pattern, replacement in replacements:
            try:
                raw_html = re.sub(pattern, replacement, raw_html).strip()
            except Exception as e:
                raise Exception(
                    f'Failed to replace `{pattern}` ({type(pattern)}) with `{replacement}` ({type(replacement)} '
                    f'in {raw_html}\n({type(raw_html)})\n{e}'
                )

        if model_instance.pk:
            raw_html = model_instance.preprocess_html(raw_html)

        # Update obj placeholders.
        # This (1) improves readability when editing and (2) reduces time to process search results.
        for content_type in self.processable_content_types:
            model_cls_str = MODEL_CLASS_PATHS.get(content_type)
            if model_cls_str:
                model_cls = import_string(model_cls_str)
                for match in model_cls.admin_placeholder_regex.finditer(raw_html):
                    placeholder = match.group(0)
                    updated_placeholder = model_cls.get_updated_placeholder(match)
                    raw_html = raw_html.replace(placeholder, updated_placeholder)

        # Wrap HTML content in a <p> tag if necessary
        if not raw_html.startswith('<') and raw_html.endswith('>'):
            raw_html = f'<p>{raw_html}</p>'

        html.raw_value = raw_html
        return html

    def deconstruct(self):
        """TODO: add docstring."""
        field_class = 'modularhistory.fields.HTMLField'
        name, path, args, kwargs = super().deconstruct()
        if self.processor != self.default_processor:
            kwargs['processor'] = self.processor
        return name, field_class, args, kwargs

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def from_db_value(self, value: Optional[str], expression, connection) -> Optional[HTML]:
        """TODO: add docstring."""
        if value is None:
            return value
        if not value.startswith('<') and value.endswith('>'):
            value = f'<p>{value}</p>'
        replacements = (
            (r'074c54e4-ff1d-4952-9964-7d1e52cec4db', '6'),
            (r'354f9d11-74bb-4e2a-8e0d-5df877b4c461', '86'),
            (r'53a517fc-68a6-42bd-ac6b-e3a84a617ace', '8'),
            (r'd8d7199b-4eaa-4189-bd29-b33dc9de4c8c', '90'),
            (r'aa7291c7-55bf-4ff0-981f-38c259bc160e', '244'),
            (r'e1e1cf34-b070-41d4-b8ba-604a3a257ace', '88'),
            (r'a662f48d-9674-4154-9d8f-3456efe7aebf', '70'),
            (r'993f6db6-c815-4521-b8a0-65e19d0dbe25', '204'),
            (r'7c86ed23-d548-4aef-81a1-1a16d6ecd7cb', '72'),
            (r'27c0d6f6-8306-4b3f-a60b-c842857ea1ab', '73'),
            (r'7579f024-9a48-4f55-b7c7-a1e88b866a0c', '246'),
            (r'260c4e8e-a35b-4306-a0ce-17cfcb7de47d', '268'),
            (r'f0af0a2b-68e5-484e-8f08-5de0179a185c', '229'),
            (r'19e0f153-b248-4147-a09b-ee35c5e4fdaf', '250'),
            (r'5610f0f6-8bba-4647-9642-e0a623c266d9', '261'),
            (r'e93eda83-560d-4a8a-8eac-8c28798b52ff', '262'),
            (r'ed35a437-15a0-4c03-9661-903db39fe216', '91'),
            (r'\n?<div[^>]+?>&nbsp;<\/div>', ''),
            (r'<div id=\"i4c-draggable-container\"[^\/]+</div>', ''),
            (r'<p>&nbsp;<\/p>', ''),
            (r'\{\{', '<<'),
            (r'\}\}', '>>'),
        )
        for pattern, replacement in replacements:
            value = re.sub(pattern, replacement, value)
        html = value
        if self.processor:
            try:
                html = self.processor(html, self.processable_content_types)
            except RecursionError as e:
                print(f'Unable to process HTML; encountered recursion error: {e}', file=stderr)
            except Exception as e:
                print(f'Unable to process HTML; encountered error: {e}\n\n{html}', file=stderr)
        return HTML(value, processed_value=html)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(self, value: Optional[Union[HTML, str]]) -> Optional[HTML]:
        """TODO: add docstring."""
        if isinstance(value, HTML):
            return value
        elif not value:
            return None
        return HTML(value)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-python-objects-to-query-values
    def get_prep_value(self, value: Optional[Union[HTML, str]]) -> Optional[str]:
        """TODO: add docstring."""
        if not value:
            return None
        elif isinstance(value, HTML):
            return value.raw_value
        return value

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-query-values-to-database-values
    def get_db_prep_value(self, value, connection, prepared=False):
        """TODO: add docstring."""
        return self.get_prep_value(value)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#id2
    def value_to_string(self, obj) -> str:
        """TODO: add docstring."""
        value = self.value_from_object(obj)
        return self.get_prep_value(value) or ''


def _get_model_class(ct: ContentType) -> Type['Model']:
    model_class = ct.model_class()
    if model_class is None:
        raise ValueError(f'Could not retrieve model class for {ct}.')
    from modularhistory.models import Model
    if not issubclass(model_class, Model):
        raise ValueError(f'{model_class} is not subclassed from custom model class.')
    return model_class


# def get_image_html(image: Union['Image', Match]):
#     """TODO: add docstring."""
#     if hasattr(image, 'group'):
#         match = image
#         key = match.group(1).strip()
#         from images.models import Image
#         try:
#             image = Image.objects.get(pk=key)
#         except ValueError as e:  # legacy key
#             print(f'{e}')
#             image = Image.objects.get(key=key)
#     image_html = render_to_string(
#         'images/_card.html',
#         context={'image': image, 'obj': image}
#     )
#     if image.width < FLOAT_UPPER_WIDTH_LIMIT:
#         image_html = f'<div class="float-right pull-right">{image_html}</div>'
#     if image.width < CENTER_UPPER_WIDTH_LIMIT:
#         image_html = f'<div style="text-align: center">{image_html}</div>'
#     return image_html
