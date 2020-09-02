# type: ignore
# TODO: remove above line after fixing typechecking
import datetime
from datetime import datetime
from typing import Optional, Union

from django.db.models import DateTimeField
from django.forms import Field
from django.utils.timezone import make_aware, is_naive

from history import settings
from history.forms import HistoricDateFormField
from history.structures.historic_datetime import HistoricDateTime

DateTime = type(datetime)


# TODO: https://dateparser.readthedocs.io/en/latest/
# TODO: https://dateutil.readthedocs.io/en/stable/
class HistoricDateTimeField(DateTimeField):
    """TODO: add docstring."""

    year: int

    def __init__(self, verbose_name=None, name=None,
                 auto_now=False, auto_now_add=False, **kwargs):
        super().__init__(verbose_name=verbose_name, name=name,
                         auto_now=auto_now, auto_now_add=auto_now_add, **kwargs)

    def clean(self, value, model_instance):
        """TODO: add docstring."""
        return super().clean(value, model_instance)

    def formfield(self, **kwargs) -> Field:
        """TODO: add docstring."""
        return super(DateTimeField, self).formfield(**{
            'form_class': HistoricDateFormField,
            **kwargs,
        })

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def from_db_value(self, value: Optional[DateTime], expression, connection) -> Optional[HistoricDateTime]:
        if value is None:
            return value
        return HistoricDateTime(value.year, value.month, value.day,
                                value.hour, value.minute, value.second, value.microsecond)

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(
            self, value: Optional[Union[HistoricDateTime, DateTime, str]]
    ) -> Optional[HistoricDateTime]:
        if not value:
            return None
        elif isinstance(value, HistoricDateTime):
            return value
        elif isinstance(value, datetime):
            return HistoricDateTime(value.year, value.month, value.day,
                                    value.hour, value.minute, value.second, value.microsecond)
        elif isinstance(value, str):
            raise TypeError

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-python-objects-to-query-values
    def get_prep_value(self, value: Optional[HistoricDateTime]) -> Optional[DateTime]:
        if not value:
            return None
        value = self.to_python(value)
        if value and settings.USE_TZ and is_naive(value):
            value = make_aware(value)
        return super().get_prep_value(value)

    #
    # # https://docs.djangoproject.com/en/3.0/howto/customg-model-fields/#converting-query-values-to-database-values
    # def get_db_prep_value(self, value, connection, prepared=False):
    #     return self.get_prep_value(value)
    #
    # # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#id2
    # def value_to_string(self, obj) -> str:
    #     value = self.value_from_object(obj)
    #     return self.get_prep_value(value) or ''
