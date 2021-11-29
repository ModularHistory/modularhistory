import logging
from typing import TYPE_CHECKING, Any, Callable, Iterable, Optional, Union

import regex as re
from aenum import Constant
from bs4.element import NavigableString, Tag
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import TextField
from django.forms.renderers import BaseRenderer
from django.forms.widgets import Textarea
from django.utils.module_loading import import_string
from django.utils.safestring import SafeText

from core.constants.content_types import MODEL_CLASS_PATHS
from core.utils.html import soupify
from core.utils.string import dedupe_newlines, truncate

if TYPE_CHECKING:
    from django.forms import Field

    from core.models.model import ExtendedModel

# group 1: entity pk
# group 2: entity name
ENTITY_NAME_REGEX = r'<span class=\"entity-name\" data-entity-id=\"(\d+)\">(.+?)</span>'

REPLACEMENTS = (
    # Prevent related videos from different channels from being displayed.
    (r'''(<iframe .*?src=["'].*youtube\.com\/[^\?]+?)(["'])''', r'\g<1>?rel=0\g<2>'),
    # Remove empty divs & paragraphs.
    (r'\n?<(?:div|p)>(?:(?:&nbsp;)+|[\s\n]+)?<\/(?:div|p)>', ''),
    # Remove <br> tags.
    (r'<br ?/?>', ''),
    # Add bootstrap classes to HTML elements.
    (r'<blockquote>', '<blockquote class="blockquote">'),
    (r'<table>', '<table class="table">'),
)
DELETIONS = (('div', {'id': 'i4c-draggable-container'}),)


class PlaceholderGroups(Constant):
    """Groups in the object placeholder regex pattern."""

    # noqa: WPS115
    # group 1: model class name
    MODEL_NAME = 'content_type'
    # group 2: model instance pk
    PK = 'key'
    # group 3: ignore
    APPENDAGE = 'appendage'
    # group 4: model instance HTML
    HTML = 'html'


START_PATTERN = r'\[\['
END_PATTERN = r'\]\]'
TYPE_GROUP = rf'(?P<{PlaceholderGroups.MODEL_NAME}>[a-zA-Z]+?)'  # noqa: WPS360
KEY_GROUP = rf'(?P<{PlaceholderGroups.PK}>[\w\d-]+)'
HTML_GROUP = rf'(?!{END_PATTERN})(?P<{PlaceholderGroups.HTML}>[^:\s][\s\S]+?)'
APPENDAGE_GROUP = rf'(?P<{PlaceholderGroups.APPENDAGE}>[:\ ,]?\ ?{HTML_GROUP})'

OBJECT_PLACEHOLDER_REGEX = rf'{START_PATTERN}\ ?{TYPE_GROUP}:\ ?{KEY_GROUP}{APPENDAGE_GROUP}?\ ?{END_PATTERN}'  # noqa: E501
logging.debug(f'Object placeholder pattern: {OBJECT_PLACEHOLDER_REGEX}')

object_placeholder_regex = re.compile(OBJECT_PLACEHOLDER_REGEX)


def process(html: str) -> str:
    """
    Return the processed version of an HTML field value.

    This involves replacing model instance placeholders with their HTML.
    """
    logging.debug(f'Processing HTML: {truncate(html)}')
    model_classes: dict[str, type['ExtendedModel']] = {}
    for match in object_placeholder_regex.finditer(html):
        placeholder = match.group(0)
        object_type = match.group(PlaceholderGroups.MODEL_NAME)
        logging.debug(f'Found {object_type} placeholder: {truncate(placeholder)}')
        model_cls_str = MODEL_CLASS_PATHS.get(object_type)
        if model_cls_str:
            model_cls: type['ExtendedModel'] = model_classes.get(
                model_cls_str, import_string(model_cls_str)
            )
            if model_cls_str not in model_classes:
                model_classes[model_cls_str] = model_cls
            logging.debug(f'Processing {object_type} placeholder: {truncate(placeholder)}')
            # TODO
            object_match = model_cls.get_admin_placeholder_regex().match(placeholder)
            if object_match:
                try:
                    object_html = model_cls.get_object_html(
                        object_match, use_preretrieved_html=True
                    )
                    logging.debug(f'Retrieved {object_type} HTML: {truncate(object_html)}')
                except ObjectDoesNotExist:
                    raise ValidationError(
                        f'Could not get HTML for placeholder: {truncate(placeholder)}'
                    )
                html = html.replace(placeholder, object_html)
            else:
                logging.error(
                    f'ERROR: {model_cls.get_admin_placeholder_regex()} '
                    f'did not match {placeholder}'
                )
        else:
            logging.info(f'ERROR: Unable to get model class string for {object_type}')
    # TODO: optimize
    html = re.sub(r'(\S)\ (<a [^>]+?citation-link)', r'\g<1>\g<2>', html)
    logging.debug(f'Successfully processed {truncate(html)}')
    return html


TRUMBOWYG_VERSION = '2.24.0'
TRUMBOWYG_CDN_BASE_URL = f'//cdnjs.cloudflare.com/ajax/libs/Trumbowyg/{TRUMBOWYG_VERSION}'


class TrumbowygWidget(Textarea):
    """Trumbowyg widget for editing HTML fields."""

    class Media:
        css = {
            'all': (
                f'{TRUMBOWYG_CDN_BASE_URL}/ui/trumbowyg.min.css',
                f'{TRUMBOWYG_CDN_BASE_URL}/plugins/table/ui/trumbowyg.table.min.css',
            )
        }
        js = (
            f'{TRUMBOWYG_CDN_BASE_URL}/trumbowyg.min.js',
            f'{TRUMBOWYG_CDN_BASE_URL}/plugins/table/trumbowyg.table.min.js',
        )

    def render(
        self,
        name: str,
        value: str,
        attrs: Optional[dict] = None,
        renderer: Optional[BaseRenderer] = None,
    ) -> SafeText:
        """Render the widget."""
        attrs = attrs or {}
        attrs['trumbowyg'] = True
        rendered_widget = super().render(name, value, attrs)
        # fmt: off
        rendered_widget += '''
            <script defer>
                window.addEventListener("load", function() {
                    (function($) { 
                        // Initialize Trumbowyg editors for HTML fields.
                        $('textarea[name="%s"]').trumbowyg({
                            resetCss: true,
                            autogrow: true,
                            autogrowOnEnter: true,
                            defaultLinkTarget: "_blank",
                            btnsDef: {
                                image: {
                                    dropdown: [
                                        "upload",
                                        "insertImage",
                                        "base64",
                                        "noembed"
                                    ],
                                    ico: "insertImage"
                                }
                            },
                            btns: [
                                ['viewHTML'],
                                ['formatting'],
                                ['strong', 'em', 'underline', 'del'],
                                ['superscript', 'subscript'],
                                ['removeformat'],
                                ['justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull'],
                                ['unorderedList', 'orderedList'],
                                ['horizontalRule'],
                                ['table'],
                                ['link'],
                                ['image'],
                                ['undo', 'redo'], // Only supported in Blink browsers
                                ['fullscreen']
                            ],
                            plugins: {},
                            tagsToRemove: ['script', 'link']
                        });
                    })(django.jQuery);
                });
            </script>
        ''' % name
        # fmt: on
        return rendered_widget


class HTMLField(TextField):
    """A field for HTML content."""

    # Callable that processes the HTML value before it is saved
    processor: Optional[Callable]

    # Whether content should be wrapped in <p> tags (if none are present)
    paragraphed: Optional[bool]

    # Types of processable objects that can be included in HTML fields
    processable_content_types: Iterable[str] = [
        'quote',
        'image',
        'citation',
        'source',
        'proposition',
    ]

    def __init__(
        self,
        *,
        paragraphed: Optional[bool] = None,
        processed: bool = True,
        processor: Optional[Callable] = None,
        **kwargs,
    ):
        """Construct an HTML field instance."""
        self.processed = processed
        self.processor = (processor or process) if processed else None
        self.paragraphed = paragraphed
        super().__init__(**kwargs)

    def clean(self, html_value: str, model_instance: Optional['ExtendedModel']) -> str:
        """Return a cleaned, ready-to-save instance of HTML."""
        html = super().clean(value=html_value, model_instance=model_instance)
        try:
            html = self._clean(html, model_instance=model_instance)
        except Exception as err:
            raise ValidationError(f'{err}')
        return html or ''

    def pre_save(self, model_instance: 'ExtendedModel', add: bool) -> str:
        """
        Modify the value immediately before saving.

        This is necessary for cases in which the `clean` method is not called; e.g.,
        if the value is modified and saved programmatically (rather than through the
        use of a model form in the Django admin site).
        """
        value: str = getattr(model_instance, self.attname, '')
        try:
            value = self._clean(value, model_instance=model_instance)
        except Exception as err:
            logging.error(f'{value=} resulted in {err=}')
        return value

    def _clean(self, value: str, model_instance: Optional['ExtendedModel']) -> str:
        value = self.format(value)
        if model_instance and model_instance.pk:
            value = model_instance.preprocess_html(value)
        value = self.update_placeholders(value)
        return value

    def formfield(self, **kwargs) -> 'Field':
        """Return the default form field for this field."""
        kwargs['widget'] = TrumbowygWidget
        return super().formfield(**kwargs)

    def make_deletions(self, html: str) -> str:
        """Delete unwanted elements from the HTML."""
        # Use html.parser to avoid automatically adding <html> and <body> tags.
        soup = soupify(html, features='html.parser')
        for deletion in DELETIONS:
            tag: Optional[Union[Tag, NavigableString]] = soup.find(*deletion)
            if isinstance(tag, Tag):
                tag.decompose()
        return str(soup)

    def make_replacements(self, html: str) -> str:
        """Make replacements in the HTML."""
        for pattern, replacement in REPLACEMENTS:
            try:
                html = re.sub(pattern, replacement, html).strip()
            except Exception as error:
                raise Exception(
                    f'Failed to replace `{pattern}` ({type(pattern)}) '
                    f'with `{replacement}` ({type(replacement)} '
                    f'in {html}\n({type(html)})\n{error}'
                )
        return html

    def format(self, html: str) -> str:
        """Add or remove <p> tags if necessary."""
        if html:
            html = html.replace('{', '[').replace('}', ']')
            html = self.make_deletions(html)
            html = dedupe_newlines(html)
            if self.paragraphed is None:
                pass
            elif self.paragraphed:
                # TODO: move this to a util method?
                if html.startswith('<p') or html.endswith('</p>'):
                    pass
                else:
                    html = f'<p>{html}</p>'
            else:  # if paragraphed is False
                # TODO: move this to a util method?
                if html.startswith('<p') and html.endswith('</p>'):
                    paragraph_strings: list[str] = [
                        p.decode_contents()
                        for p in soupify(html).find_all('p')
                        if isinstance(p, Tag)
                    ]
                    if not paragraph_strings:
                        raise Exception(f'Failed to parse paragraphs in HTML: {html}')
                    html = ' '.join(paragraph_strings)
            html = self.make_replacements(html)
        return html

    def update_placeholders(self, html: str) -> str:
        """
        Modify object placeholders to include up-to-date HTML representations.

        Including HTML in the placeholders (1) improves readability when editing
        and (2) reduces time to process search results.
        """
        soup = soupify(html)
        referenced_modules = soup.find_all('module')
        for referenced_module in referenced_modules:
            print(referenced_module)
        for content_type in self.processable_content_types:
            model_cls_str = MODEL_CLASS_PATHS.get(content_type)
            if model_cls_str:
                model_cls: type['ExtendedModel'] = import_string(model_cls_str)
                for match in model_cls.get_admin_placeholder_regex().finditer(html):
                    if match.group(PlaceholderGroups.MODEL_NAME) != content_type:
                        logging.error(
                            f'{match.group(0)} is not an instance of {content_type}.'
                        )
                        continue
                    placeholder = match.group(0)
                    try:
                        updated_placeholder = model_cls.get_updated_placeholder(match)
                        html = html.replace(placeholder, updated_placeholder)
                    except ObjectDoesNotExist as err:
                        raise ValueError(
                            f'Unable to retrieve object matching {match.group(0)}'
                        ) from err
        return html

    def deconstruct(self) -> tuple:
        """
        Return a 4-tuple with enough information to recreate the field.

        https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.deconstruct
        """
        field_class = 'core.fields.HTMLField'
        name, path, args, kwargs = super().deconstruct()
        kwargs['processed'] = getattr(self, 'processed', self.processor is not None)
        kwargs['processor'] = self.processor
        kwargs['paragraphed'] = self.paragraphed
        return name, field_class, args, kwargs

    def from_db_value(self, html_value: Optional[str], *args) -> str:
        """
        Convert a value as returned by the database to a Python object.

        This method is the reverse of get_prep_value().
        https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.from_db_value
        """
        if html_value is None:
            return ''
        return html_value

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.to_python
    def to_python(self, html_value: Optional[str]) -> str:
        """Convert the value into the correct Python object."""
        if html_value is None:
            return ''
        return html_value

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.get_prep_value
    def get_prep_value(self, html_value: Optional[str]) -> str:
        """Return data in a format prepared for use as a parameter in a db query."""
        if html_value is None:
            return ''
        return html_value

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.get_db_prep_value
    def get_db_prep_value(self, html_value: Optional[str], *args, **kwargs) -> str:
        """Convert the value to a backend-specific value."""
        return self.get_prep_value(html_value)

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.value_to_string
    def value_to_string(self, html_object: Any) -> str:
        """Convert the object to a string."""
        html_value = self.value_from_object(html_object)
        return self.get_prep_value(html_value) or ''
