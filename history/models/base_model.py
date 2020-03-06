from typing import Any, List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model as BaseModel
from django.urls import reverse
from polymorphic.models import PolymorphicModel as BasePolymorphicModel

from .manager import Manager, PolymorphicManager


class Model(BaseModel):
    objects: Manager = Manager()
    searchable_fields: Optional[List] = None

    @classmethod
    def get_searchable_fields(cls) -> List:
        return cls.searchable_fields or []

    @property
    def ctype(self) -> ContentType:
        return ContentType.objects.get_for_model(self)

    @property
    def natural_key_fields(self) -> Optional[List]:
        unique_together = getattr(self.Meta, 'unique_together', None)
        if unique_together:
            if not (isinstance(unique_together, (list, tuple))
                    and all([isinstance(v, str) for v in unique_together])):
                raise ValueError('The `unique_together` value must be an iterable containing strings.')
            return unique_together
        else:
            fields = self._meta.get_fields()
            unique_fields = []
            for field in fields:
                if getattr(field, 'unique', False):
                    unique_fields.append(field.name)
            if unique_fields:
                return unique_fields
        raise NotImplementedError('Model must have Meta.unique_together and/or `natural_key_fields` method defined.')

    def get_admin_url(self):
        return reverse(f'admin:{self._meta.app_label}_{self._meta.model_name}_change', args=[self.id])

    def natural_key(self) -> Tuple[Any]:
        natural_key_fields = self.natural_key_fields
        natural_key_values = []
        for field in natural_key_fields:
            value = getattr(self, field, None)
            if not value:
                raise AttributeError(f'Model has no `{field}` attribute.')
            natural_key_values.append(value)
        return tuple(value for value in natural_key_values)

    class Meta:
        abstract = True


class PolymorphicModel(BasePolymorphicModel, Model):
    objects = PolymorphicManager()

    class Meta:
        abstract = True

    @property
    def ctype(self) -> ContentType:
        return self.polymorphic_ctype

    def get_admin_url(self):
        return reverse(f'admin:{self.ctype.app_label}_{self.ctype.model}_change', args=[self.id])
