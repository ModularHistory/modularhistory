"""ModularHistory's HistoricDateTimeField (for use in models)."""

from datetime import datetime
from typing import Optional, Union

from django.db.models import DateTimeField
from django.forms import Field
from django.utils.timezone import make_aware, is_naive

from history import settings
from history.forms import HistoricDateFormField
from history.structures.historic_datetime import HistoricDateTime

DateTime = datetime


# TODO: https://dateparser.readthedocs.io/en/latest/
# TODO: https://dateutil.readthedocs.io/en/stable/
class HistoricDateTimeField(DateTimeField):
    """TODO: add docstring."""

    year: int

    def __init__(
        self,
        verbose_name=None,
        name=None,
        auto_now=False,
        auto_now_add=False,
        **kwargs
    ):
        """TODO: add docstring."""
        super().__init__(
            verbose_name=verbose_name,
            name=name,
            auto_now=auto_now,
            auto_now_add=auto_now_add,
            **kwargs
        )

    def formfield(self, **kwargs) -> Field:
        """TODO: add docstring."""
        return super(DateTimeField, self).formfield(**{
            'form_class': HistoricDateFormField,
            **kwargs,
        })

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def from_db_value(
        self,
        value: Optional[DateTime],
        expression,
        connection
    ) -> Optional[HistoricDateTime]:
        """TODO: add docstring."""
        if value is None:
            return value
        return HistoricDateTime(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond
        )

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(
        self,
        value: Optional[Union[HistoricDateTime, DateTime, str]]
    ) -> Optional[HistoricDateTime]:
        """TODO: add docstring."""
        if not value:
            return None
        elif isinstance(value, HistoricDateTime):
            return value
        elif isinstance(value, datetime):
            return HistoricDateTime(
                value.year,
                value.month,
                value.day,
                value.hour,
                value.minute,
                value.second,
                value.microsecond
            )
        elif isinstance(value, str):
            raise TypeError

    # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#converting-python-objects-to-query-values
    def get_prep_value(
        self,
        value: Optional[HistoricDateTime]
    ) -> Optional[DateTime]:
        """TODO: add docstring."""
        if not value:
            return None
        preprep_value: Union[HistoricDateTime, DateTime] = self.to_python(value)
        if preprep_value and settings.USE_TZ and is_naive(preprep_value):
            preprep_value = make_aware(preprep_value)
        return super().get_prep_value(preprep_value)

    #
    # # https://docs.djangoproject.com/en/3.0/howto/customg-model-fields/#converting-query-values-to-database-values
    # def get_db_prep_value(self, value, connection, prepared=False):
    #     return self.get_prep_value(value)
    #
    # # https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/#id2
    # def value_to_string(self, obj) -> str:
    #     value = self.value_from_object(obj)
    #     return self.get_prep_value(value) or ''
