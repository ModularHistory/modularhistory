from typing import Any, List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model as BaseModel
from django.urls import reverse
from django.utils.safestring import SafeText, mark_safe
from polymorphic.models import PolymorphicModel as BasePolymorphicModel

from history.models.manager import Manager, PolymorphicManager


class Model(BaseModel):
    """TODO: add docstring."""

    objects: Manager = Manager()
    searchable_fields: Optional[List] = None

    @classmethod
    def get_searchable_fields(cls) -> List:
        """TODO: add docstring."""
        return cls.searchable_fields or []

    @property
    def admin_url(self) -> str:
        """TODO: add docstring."""
        return self.get_admin_url()

    @property
    def ctype(self) -> ContentType:
        """TODO: add docstring."""
        return ContentType.objects.get_for_model(self)

    @property
    def detail_link(self) -> SafeText:
        """TODO: add docstring."""
        return self.get_detail_link()

    @property
    def detail_url(self) -> str:
        """TODO: add docstring."""
        return reverse(f'{self._meta.app_label}:detail', args=[self.id])

    @property
    def natural_key_fields(self) -> Optional[List]:
        """TODO: add docstring."""
        unique_together = getattr(self.Meta, 'unique_together', None)
        if unique_together:
            if not (isinstance(unique_together, (list, tuple))
                    and all([isinstance(v, str) for v in unique_together])):
                raise ValueError('The `unique_together` value must be '
                                 'an iterable containing strings.')
            return unique_together
        else:
            fields = self._meta.get_fields()
            unique_fields = []
            for field in fields:
                if getattr(field, 'unique', False):
                    unique_fields.append(field.name)
            if unique_fields:
                return unique_fields
        raise NotImplementedError('Model must have Meta.unique_together '
                                  'and/or `natural_key_fields` method defined.')

    def get_admin_url(self):
        """TODO: add docstring."""
        return reverse(f'admin:{self._meta.app_label}_{self._meta.model_name}_change',
                       args=[self.id])

    def get_detail_link(self) -> SafeText:
        """TODO: add docstring."""
        return mark_safe(f'<a href="{self.detail_url}" target="_blank">'
                         f'<i class="fas fa-info-circle"></i></a>')

    def natural_key(self) -> Tuple[Any]:
        """TODO: add docstring."""
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
    """TODO: add docstring."""

    objects = PolymorphicManager()

    class Meta:
        abstract = True

    @property
    def ctype(self) -> ContentType:
        """TODO: add docstring."""
        return ContentType.objects.get_for_id(self.polymorphic_ctype_id)

    @property
    def detail_url(self) -> str:
        """TODO: add docstring."""
        return reverse(f'{self.ctype.app_label}:detail', args=[self.id])

    def get_admin_url(self):
        """TODO: add docstring."""
        return reverse(f'admin:{self.ctype.app_label}_{self.ctype.model}_change',
                       args=[self.id])
