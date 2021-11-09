from rest_framework.fields import DateTimeField as DrfDateTimeField

from apps.dates.structures import HistoricDateTime


class HistoricDateTimeDrfField(DrfDateTimeField):
    """Serializer field for historic datetimes."""

    def to_internal_value(self, value) -> HistoricDateTime:
        value = super().to_internal_value(value)
        value = HistoricDateTime(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond,
            tzinfo=value.tzinfo,
        )
        return value
