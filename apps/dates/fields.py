"""ModularHistory's HistoricDateTimeField (for use in models)."""

from datetime import datetime as DateTime  # noqa: N812
from typing import Optional, Union

import serpy
from dateutil.parser import isoparse
from django.db.models import DateTimeField

from apps.dates.structures import HistoricDateTime


class HistoricDateTimeField(DateTimeField):
    """Model field for historic datetimes."""

    year: int

    # https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.Field.from_db_value
    def from_db_value(self, value: Optional[DateTime], *args) -> Optional[HistoricDateTime]:
        """
        Convert a value as returned by the database to a Python object.

        This method is the reverse of get_prep_value().
        """
        if value is None:
            return value
        return HistoricDateTime(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond,
            tzinfo=value.tzinfo,
        )

    # https://docs.djangoproject.com/en/dev/howto/custom-model-fields/#converting-values-to-python-objects
    def to_python(self, value: Optional[Union[DateTime, str]]) -> Optional[HistoricDateTime]:
        """
        Convert the value into the correct Python object.

        This method acts as the reverse of value_to_string(), and is also called in clean().
        """
        if not value:
            return None
        elif isinstance(value, HistoricDateTime):
            return value
        elif isinstance(value, str):
            value = isoparse(value)
        return HistoricDateTime(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond,
            tzinfo=value.tzinfo,
        )

    # https://docs.djangoproject.com/en/dev/howto/custom-model-fields/#converting-python-objects-to-query-values
    def get_prep_value(self, value: Optional[HistoricDateTime]) -> Optional[DateTime]:
        """
        Return data in a format prepared for use a db query parameter.

        `value` is the current value of the model’s attribute.
        """
        preprep_value = self.to_python(value)
        if preprep_value:
            return super().get_prep_value(preprep_value)
        return None


class TimelinePositionField(serpy.Field):
    """Represents dates on a continuous floating point scale."""

    def to_value(self, value: HistoricDateTime):
        return value.timeline_position
