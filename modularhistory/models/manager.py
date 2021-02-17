"""Manager classes for ModularHistory's models."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional, Union

from django.db.models import Manager as ModelManager
from typedmodels.models import TypedModelManager as BaseTypedModelManager

from modularhistory.structures.historic_datetime import HistoricDateTime

if TYPE_CHECKING:
    from modularhistory.models import Model


class Manager(ModelManager):
    """Base manager for ModularHistory's models."""

    def get_by_natural_key(self, *args):
        """Retrieva model instance by its natural key."""
        fields = self.model.natural_key_fields
        natural_key = {}
        for index, field in enumerate(fields):
            natural_key[field] = args[index]
        return self.get(**natural_key)

    def get_closest_to_datetime(
        self,
        datetime_value: Union[date, datetime, HistoricDateTime],
        datetime_attr: str = 'date',
    ) -> Optional['Model']:
        """Return the model instance closest to the specified datetime_value."""
        qs = self.get_queryset()
        greater = qs.filter(date__gte=datetime_value).order_by(datetime_attr).first()
        lesser = (
            qs.filter(date__lte=datetime_value).order_by(f'-{datetime_attr}').first()
        )
        if not greater and not lesser:  # TODO
            return qs.first()
        elif greater and lesser:
            greater_diff = abs(getattr(greater, datetime_attr) - datetime_value)
            lesser_diff = abs(getattr(lesser, datetime_attr) - datetime_value)
            return greater if greater_diff < lesser_diff else lesser
        return greater or lesser


class TypedModelManager(BaseTypedModelManager, Manager):
    """Wrapper for TypedModelManager."""

    pass  # noqa: WPS604
