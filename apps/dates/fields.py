"""ModularHistory's HistoricDateTimeField (for use in models)."""

from datetime import datetime
from typing import Optional, Union

from django.db.models import DateTimeField
from django.forms import Field

from apps.dates.structures import HistoricDateTime
from core.forms import HistoricDateFormField

DateTime = datetime


# TODO: https://dateparser.readthedocs.io/en/latest/
# TODO: https://dateutil.readthedocs.io/en/stable/
class HistoricDateTimeField(DateTimeField):
    """Model field for historic datetimes."""

    year: int

    def formfield(self, **kwargs) -> Field:
        """Return the form field to be used for historic datetimes."""
        return super(DateTimeField, self).formfield(
            **{
                'form_class': HistoricDateFormField,
                **kwargs,
            }
        )

    def from_db_value(
        self, datetime_value: Optional[DateTime], expression, connection
    ) -> Optional[HistoricDateTime]:
        """
        Convert a value as returned by the database to a Python object.

        This method is the reverse of get_prep_value().

        https://docs.djangoproject.com/en/3.1/ref/models/fields/#django.db.models.Field.from_db_value
        """
        if datetime_value is None:
            return datetime_value
        # TODO: include tz? It's set to UTC by default in HistoricDateTime.__new__.
        return HistoricDateTime(
            datetime_value.year,
            datetime_value.month,
            datetime_value.day,
            datetime_value.hour,
            datetime_value.minute,
            datetime_value.second,
            datetime_value.microsecond,
        )

    # https://docs.djangoproject.com/en/3.1/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(
        self, historic_datetime: Optional[Union[DateTime, str]]
    ) -> Optional[HistoricDateTime]:
        """
        Convert the value into the correct Python object.

        This method acts as the reverse of value_to_string(), and is also called in clean().
        """
        if not historic_datetime:
            return None
        elif isinstance(historic_datetime, str):
            raise TypeError
        if isinstance(historic_datetime, HistoricDateTime):
            return historic_datetime
        elif isinstance(historic_datetime, datetime):
            return HistoricDateTime(
                historic_datetime.year,
                historic_datetime.month,
                historic_datetime.day,
                historic_datetime.hour,
                historic_datetime.minute,
                historic_datetime.second,
                historic_datetime.microsecond,
            )

    # https://docs.djangoproject.com/en/3.1/howto/custom-model-fields/#converting-python-objects-to-query-values
    def get_prep_value(
        self, historic_datetime: Optional[HistoricDateTime]
    ) -> Optional[DateTime]:
        """
        Return data in a format prepared for use a db query parameter.

        `value` is the current value of the model’s attribute.
        """
        preprep_value = self.to_python(historic_datetime)
        if preprep_value:
            return super().get_prep_value(preprep_value)
        return None
