import datetime
import os
from datetime import datetime
from functools import partial
from typing import Optional, Union

# from sys import stderr
from django.contrib.postgres.fields import ArrayField as PostgresArrayField
from django.db.models import DateField, DateTimeField, FileField
from django.forms import Field
from django.utils.safestring import SafeText
from tinymce.models import HTMLField as MceHTMLField

from history.forms import HistoricDateFormField, SimpleArrayField, SourceFileFormField
from history.structures.historic_datetime import HistoricDateTime
from history.structures.html import HTML
from history.structures.source_file import SourceFile


def _update_filename(instance, filename, path):
    path, filename = path, filename
    return os.path.join(path, filename)


def upload_to(path):
    return partial(_update_filename, path=path)


class SourceFileField(FileField):
    attr_class = SourceFile

    def formfield(self, **kwargs) -> Field:
        return super(FileField, self).formfield(**{
            'form_class': SourceFileFormField,
            **kwargs,
        })


class ArrayField(PostgresArrayField):
    def formfield(self, **kwargs) -> Field:
        return super(PostgresArrayField, self).formfield(**{
            'form_class': SimpleArrayField,
            'base_field': self.base_field.formfield(),
            'max_length': self.size,
            **kwargs,
        })


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
    year: int

    def __init__(self, verbose_name=None, name=None, auto_now=False, auto_now_add=False, **kwargs):
        super().__init__(verbose_name=verbose_name, name=name, auto_now=auto_now, auto_now_add=auto_now_add, **kwargs)

    def formfield(self, **kwargs) -> Field:
        return super(DateTimeField, self).formfield(**{
            'form_class': HistoricDateFormField,
            **kwargs,
        })

    # def clean(self, value, model_instance) -> HTML:
    #     value = super().clean(value=value, model_instance=model_instance)
    #     value.raw_html = value.raw_html.replace('<blockquote>', '<blockquote class="blockquote">')
    #     return value

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def from_db_value(self, value: Optional[datetime], expression, connection) -> Optional[HistoricDateTime]:
        if value is None:
            return value
        return HistoricDateTime(value.year, value.month, value.day, value.hour, value.minute, value.second)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(self, value: Optional[Union[HistoricDateTime, datetime, str]]) -> Optional[HistoricDateTime]:
        if not value:
            return None
        elif isinstance(value, HistoricDateTime):
            return value
        elif isinstance(value, datetime):
            return HistoricDateTime(value.year, value.month, value.day, value.hour, value.minute, value.second)
        elif isinstance(value, str):
            raise TypeError

    # # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-python-objects-to-query-values
    # def get_prep_value(self, value: Optional[HistoricDateTime]) -> Optional[datetime]:
    #     if isinstance(value, HistoricDateTime):
    #         return datetime(value.year, value.month, value.day, value.hour, value.minute, value.second)
    #     elif not value:
    #         return None
    #
    # # https://docs.djangoproject.com/en/3.0/howto/customg-model-fields/#converting-query-values-to-database-values
    # def get_db_prep_value(self, value, connection, prepared=False):
    #     return self.get_prep_value(value)
    #
    # # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#id2
    # def value_to_string(self, obj) -> str:
    #     value = self.value_from_object(obj)
    #     return self.get_prep_value(value) or ''
