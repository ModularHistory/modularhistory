"""Base model classes for ModularHistory."""

from typing import Any, ClassVar, List, Optional, Pattern, TYPE_CHECKING, Tuple, Type

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model as DjangoModel
from django.urls import reverse
from django.utils.html import SafeString, format_html
# from polymorphic.models import PolymorphicModel as BasePolymorphicModel
from typedmodels.models import TypedModel as BaseTypedModel

from history.models.manager import Manager  # , PolymorphicManager

if TYPE_CHECKING:
    from re import Match

FieldList = List[str]

# TODO: Extend BaseTypedModel when it's possible.
# Currently, only one level of inheritance from BaseTypedModel is permitted, unfortunately.
TypedModel: Type[BaseTypedModel] = BaseTypedModel


class Model(DjangoModel):
    """TODO: add docstring."""

    objects: Manager = Manager()
    searchable_fields: ClassVar[Optional[FieldList]] = None

    admin_placeholder_regex: Pattern

    class Meta:
        abstract = True

    @classmethod
    def get_searchable_fields(cls) -> FieldList:
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
    def detail_link(self) -> SafeString:
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
            unique_together_is_valid = (
                isinstance(unique_together, (list, tuple)) and
                all(isinstance(v, str) for v in unique_together)
            )
            if not unique_together_is_valid:
                raise ValueError('The `unique_together` value must be an iterable containing strings.')
            return list(unique_together)
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
        """TODO: add docstring."""
        return reverse(
            f'admin:{self._meta.app_label}_{self._meta.model_name}_change',
            args=[self.id]
        )

    def get_detail_link(self) -> SafeString:
        """TODO: add docstring."""
        return format_html(
            f'<a href="{self.detail_url}" target="_blank">'
            f'<i class="fas fa-info-circle"></i></a>'
        )

    def natural_key(self) -> Tuple[Any, ...]:
        """TODO: add docstring."""
        natural_key_values = []
        for field in self.natural_key_fields:
            value = getattr(self, field, None)
            if not value:
                raise AttributeError(f'Model has no `{field}` attribute.')
            natural_key_values.append(value)
        return tuple(natural_key_values)

    @classmethod
    def get_object_html(cls, match: 'Match', use_preretrieved_html: bool) -> str:
        """Must be implemented in inheriting model classes."""
        raise NotImplementedError

    @classmethod
    def get_updated_placeholder(cls, match: 'Match') -> str:
        """Must be implemented in inheriting model classes."""
        raise NotImplementedError


# class PolymorphicModel(BasePolymorphicModel, Model):
#     """TODO: add docstring."""
#
#     objects = PolymorphicManager()
#
#     class Meta:
#         abstract = True
#
#     @property
#     def ctype(self) -> ContentType:
#         """TODO: add docstring."""
#         return ContentType.objects.get_for_id(self.polymorphic_ctype_id)
#
#     @property
#     def detail_url(self) -> str:
#         """TODO: add docstring."""
#         return reverse(f'{self.ctype.app_label}:detail', args=[self.id])
#
#     def get_admin_url(self):
#         """TODO: add docstring."""
#         return reverse(
#             f'admin:{self.ctype.app_label}_{self.ctype.model}_change',
#             args=[self.id]
#         )
