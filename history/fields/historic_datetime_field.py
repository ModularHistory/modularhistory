import datetime
from datetime import datetime
from typing import Optional, Union

# from sys import stderr
from django.db.models import DateField, DateTimeField
from django.forms import Field

from history.forms import HistoricDateFormField
from history.structures.historic_datetime import HistoricDateTime


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
        super().__init__(verbose_name=verbose_name, name=name, auto_now=auto_now, auto_now_add=auto_now_add,
                         **kwargs)

    def formfield(self, **kwargs) -> Field:
        return super(DateTimeField, self).formfield(**{
            'form_class': HistoricDateFormField,
            **kwargs,
        })

    # def clean(self, value, model_instance) -> HTML:
    #     value = super().clean(value=value, model_instance=model_instance)
    #     value.raw_value = value.raw_value.replace('<blockquote>', '<blockquote class="blockquote">')
    #     return value

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def from_db_value(self, value: Optional[datetime], expression, connection) -> Optional[HistoricDateTime]:
        if value is None:
            return value
        return HistoricDateTime(value.year, value.month, value.day,
                                value.hour, value.minute, value.second, value.microsecond)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(self, value: Optional[Union[HistoricDateTime, datetime, str]]) -> Optional[HistoricDateTime]:
        if not value:
            return None
        elif isinstance(value, HistoricDateTime):
            return value
        elif isinstance(value, datetime):
            return HistoricDateTime(value.year, value.month, value.day,
                                    value.hour, value.minute, value.second, value.microsecond)
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