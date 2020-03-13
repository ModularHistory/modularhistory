import datetime
from datetime import datetime
from typing import Optional, Union

from django.db.models import DateTimeField
from django.forms import Field, ValidationError

from history.forms import HistoricDateFormField
from history.structures.historic_datetime import HistoricDateTime


# TODO: https://dateparser.readthedocs.io/en/latest/
# TODO: https://dateutil.readthedocs.io/en/stable/
class HistoricDateTimeField(DateTimeField):
    year: int

    def __init__(self, verbose_name=None, name=None, auto_now=False, auto_now_add=False, **kwargs):
        super().__init__(verbose_name=verbose_name, name=name, auto_now=auto_now, auto_now_add=auto_now_add,
                         **kwargs)

    def clean(self, value, model_instance):
        print(f'>>> before HistoricDateTimeField clean: {value}')
        try:
            value = super().clean(value, model_instance)
        except ValidationError as e:
            raise ValidationError(f'HistoricDateTimeField validation error: {e}')
        print(f'>>> after HistoricDateTimeField clean: {value}')
        return value

    def formfield(self, **kwargs) -> Field:
        return super(DateTimeField, self).formfield(**{
            'form_class': HistoricDateFormField,
            **kwargs,
        })

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
