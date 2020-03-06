from typing import Optional, Union

# from sys import stderr
from django.utils.safestring import SafeText
from tinymce.models import HTMLField as MceHTMLField

from history.structures.html import HTML


class HTMLField(MceHTMLField):
    """A string field for HTML content; uses the TinyMCE widget in forms."""
    raw_html: str
    html: SafeText
    text: str

    def clean(self, value, model_instance) -> HTML:
        value = super().clean(value=value, model_instance=model_instance)
        value.raw_html = value.raw_html.replace(
            '<blockquote>', '<blockquote class="blockquote">'
        ).replace(
            '<table>', '<table class="table">'
        )

        return value

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def from_db_value(self, value: Optional[str], expression, connection) -> Optional[HTML]:
        if value is None:
            return value
        return HTML(value)

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
            return value.raw_html
        elif not value:
            return None

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-query-values-to-database-values
    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#id2
    def value_to_string(self, obj) -> str:
        value = self.value_from_object(obj)
        return self.get_prep_value(value) or ''
