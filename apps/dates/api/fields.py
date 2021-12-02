from rest_framework.fields import DateTimeField as DrfDateTimeField

from apps.dates.structures import HistoricDateTime


class HistoricDateTimeField(DrfDateTimeField):
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


class TimelinePositionField(HistoricDateTimeField):
    """Represents dates on a continuous floating point scale."""

    def to_representation(self, value: HistoricDateTime):
        return value.timeline_position
