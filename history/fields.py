from typing import Optional, Union

# from sys import stderr
from bs4 import BeautifulSoup
from django.contrib.postgres.fields import ArrayField as PostgresArrayField
from django.forms import Field
from history.forms import HistoricDateFormField, HistoricDateFormField
from django.db.models import DateField, DateTimeField
from django.utils.safestring import SafeText, mark_safe
from tinymce.models import HTMLField as MceHTMLField
from datetime import date, datetime
from history.forms import SimpleArrayField


class ArrayField(PostgresArrayField):
    def formfield(self, **kwargs) -> Field:
        return super(PostgresArrayField, self).formfield(**{
            'form_class': SimpleArrayField,
            'base_field': self.base_field.formfield(),
            'max_length': self.size,
            **kwargs,
        })


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


class HTMLField(MceHTMLField):
    """A string field for HTML content; uses the TinyMCE widget in forms."""
    raw_html: str
    html: SafeText
    text: str

    def clean(self, value, model_instance) -> HTML:
        value = super().clean(value=value, model_instance=model_instance)
        value.raw_html = value.raw_html.replace('<blockquote>', '<blockquote class="blockquote">')
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


class HistoricDate(date):
    pass


class HistoricDateTime(datetime):
    pass


# TODO: https://dateparser.readthedocs.io/en/latest/
# TODO: https://dateutil.readthedocs.io/en/stable/
# https://softwareengineering.stackexchange.com/questions/194286/how-do-you-store-fuzzy-dates-into-a-database
class HistoricDateField(DateField):
    def formfield(self, **kwargs) -> Field:
        return super(DateField, self).formfield(**{
            'form_class': HistoricDateFormField,
            **kwargs,
        })


class HistoricDateTimeField(DateTimeField):
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     raise NotImplementedError

    def formfield(self, **kwargs) -> Field:
        return super(DateTimeField, self).formfield(**{
            'form_class': HistoricDateFormField,
            **kwargs,
        })
