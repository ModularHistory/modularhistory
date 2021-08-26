import logging
from typing import TYPE_CHECKING, Callable, Optional, Sequence, Union

from django.contrib.admin import StackedInline as BaseStackedInline
from django.contrib.admin import TabularInline as BaseTabularInline
from django.core.exceptions import FieldDoesNotExist, FieldError

from apps.admin.model_admin import FORM_FIELD_OVERRIDES

if TYPE_CHECKING:
    from django.db.models import Model
    from django.http import HttpRequest

    from core.models.model import ExtendedModel


FIELDS_EXCLUDED_FROM_INLINES = (
    'deleted',
    'verified',
)


class StackedInline(BaseStackedInline):
    """Inline admin with fields stacked vertically."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    def get_fields(
        self, request: 'HttpRequest', obj: Optional['Model']
    ) -> Sequence[Union[Callable, str]]:
        return [
            field
            for field in super().get_fields(request, obj=obj)
            if field not in FIELDS_EXCLUDED_FROM_INLINES
        ]


class TabularInline(BaseTabularInline):
    """Inline admin with fields laid out horizontally."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    def get_extra(
        self,
        request: 'HttpRequest',
        obj: Optional['ExtendedModel'] = None,
        **kwargs,
    ) -> int:
        """Return the number of extra/blank rows to display."""
        if self.extra == 0:
            return self.extra
        if obj:
            if self.fk_name:
                fk_name = self.fk_name
            elif hasattr(self.model, 'content_object'):
                fk_name = 'content_object'
            else:
                fk_name = get_fk_name(obj)
            try:
                if len(self.get_queryset(request).filter(**{f'{fk_name}_id': obj.pk})):
                    return 0
            except (FieldError, FieldDoesNotExist) as err:
                logging.error(err)
        return 1

    def get_fields(
        self, request: 'HttpRequest', obj: Optional['Model']
    ) -> Sequence[Union[Callable, str]]:
        return [
            field
            for field in super().get_fields(request, obj=obj)
            if field not in FIELDS_EXCLUDED_FROM_INLINES
        ]


def get_fk_name(model_instance: 'ExtendedModel') -> str:
    if model_instance._meta.proxy_for_model:
        fk_name = model_instance._meta.proxy_for_model.__name__
    elif getattr(model_instance, 'polymorphic_ctype_id', None):
        fk_name = list(model_instance.__class__._meta.parents.keys())[0].__name__
    elif model_instance._meta.model_name:
        fk_name = model_instance._meta.model_name
    else:
        raise Exception('Unable to determine foreign key field name.')
    return fk_name.lower()
