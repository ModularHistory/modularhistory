import re
from sys import stderr
from typing import Any, Callable, Iterable, Optional, TYPE_CHECKING, Type, Union

from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string
from django.utils.safestring import SafeString
from tinymce.models import HTMLField as MceHTMLField

from modularhistory.constants import EMPTY_STRING, MODEL_CLASS_PATHS
from modularhistory.structures.html import HTML

if TYPE_CHECKING:
    from modularhistory.models import Model

# group 1: entity pk
# group 2: entity name
ENTITY_NAME_REGEX = r'<span class=\"entity-name\" data-entity-id=\"(\d+)\">(.+?)</span>'

# group 1: obj type
OBJECT_REGEX = re.compile(r'<< ?(\w+):(?!>>)[\s\S]+? ?>>')


def process(_, html: str, processable_content_types: Iterable[str]) -> str:
    """
    Return the processed version of an HTML field value.
    This involves replacing model instance placeholders with their HTML.
    """
    for match in OBJECT_REGEX.finditer(html):
        placeholder = match.group(0)
        object_type = match.group(1)
        model_cls_str = MODEL_CLASS_PATHS.get(object_type)
        if model_cls_str:
            model_cls: Type[Model] = import_string(model_cls_str)
            # TODO
            object_match = model_cls.admin_placeholder_regex.match(placeholder)
            object_html = model_cls.get_object_html(
                object_match, use_preretrieved_html=True
            )
            html = html.replace(placeholder, object_html)
        else:
            print(
                f'Unable to retrieve model class string for `{object_type}`',
                file=stderr,
            )
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
        """Construct an HTML field instance."""
        processor = kwargs.pop('processor', None)
        if processor and processor != self.default_processor:
            self.processor = processor
        super().__init__(*args, **kwargs)

    def clean(self, html_value, model_instance: 'Model') -> HTML:
        """Return a cleaned, ready-to-save instance of HTML."""
        html = super().clean(value=html_value, model_instance=model_instance)
        raw_html = html.raw_value
        replacements = (
            (r'<blockquote>', '<blockquote class="blockquote">'),
            (r'<table>', '<table class="table">'),
            # Remove empty divs
            (r'\n?<div[^>]+?>&nbsp;<\/div>', EMPTY_STRING),
            (r'<div id=\"i4c-draggable-container\"[^\/]+</div>', EMPTY_STRING),
            (r'<p>&nbsp;<\/p>', EMPTY_STRING),
        )
        for pattern, replacement in replacements:
            try:
                raw_html = re.sub(pattern, replacement, raw_html).strip()
            except Exception as error:
                raise Exception(
                    f'Failed to replace `{pattern}` ({type(pattern)}) '
                    f'with `{replacement}` ({type(replacement)} '
                    f'in {raw_html}\n({type(raw_html)})\n{error}'
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
        """
        Return a 4-tuple with enough information to recreate the field.
        https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.Field.deconstruct
        """
        field_class = 'modularhistory.fields.HTMLField'
        name, path, args, kwargs = super().deconstruct()
        if self.processor != self.default_processor:
            kwargs['processor'] = self.processor
        return name, field_class, args, kwargs

    def from_db_value(
        self, html_value: Optional[str], expression, connection
    ) -> Optional[HTML]:
        """
        Convert a value as returned by the database to a Python object.
        It is the reverse of get_prep_value().
        https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.Field.from_db_value
        """
        if html_value is None:
            return html_value
        if not html_value.startswith('<') and html_value.endswith('>'):
            html_value = f'<p>{html_value}</p>'
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
            (r'\n?<div[^>]+?>&nbsp;<\/div>', EMPTY_STRING),
            (r'<div id=\"i4c-draggable-container\"[^\/]+</div>', EMPTY_STRING),
            (r'<p>&nbsp;<\/p>', EMPTY_STRING),
            (r'\{\{', '<<'),
            (r'\}\}', '>>'),
        )
        for pattern, replacement in replacements:
            html_value = re.sub(pattern, replacement, html_value)
        processed_html = html_value
        if self.processor:
            try:
                processed_html = self.processor(
                    html_value, self.processable_content_types
                )
            except RecursionError as error:
                print(f'Unable to process HTML: {error}', file=stderr)
            except Exception as error:
                print(f'Unable to process HTML: {error}\n\n{html_value}', file=stderr)
        return HTML(html_value, processed_value=processed_html)

    # https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.Field.to_python
    def to_python(self, html_value: Optional[Union[HTML, str]]) -> Optional[HTML]:
        """Convert the value into the correct Python object."""
        if isinstance(html_value, HTML):
            return html_value
        elif not html_value:
            return None
        return HTML(html_value)

    # https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.Field.get_prep_value
    def get_prep_value(self, html_value: Optional[Union[HTML, str]]) -> Optional[str]:
        """Return data in a format prepared for use as a parameter in a db query."""
        if not html_value:
            return None
        elif isinstance(html_value, HTML):
            return html_value.raw_value
        return html_value

    # https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.Field.get_db_prep_value
    def get_db_prep_value(self, html_value, connection, prepared=False):
        """Convert the value to a backend-specific value."""
        return self.get_prep_value(html_value)

    # https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.Field.value_to_string
    def value_to_string(self, html_object: Any) -> str:
        """Convert the object to a string."""
        html_value = self.value_from_object(html_object)
        return self.get_prep_value(html_value) or EMPTY_STRING


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
