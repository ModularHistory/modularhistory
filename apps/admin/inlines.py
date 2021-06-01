import logging
from typing import TYPE_CHECKING, Optional

from django.contrib.admin import StackedInline as BaseStackedInline
from django.contrib.admin import TabularInline as BaseTabularInline
from django.core.exceptions import FieldDoesNotExist, FieldError

from apps.admin.model_admin import FORM_FIELD_OVERRIDES

if TYPE_CHECKING:
    from django.http import HttpRequest

    from core.models.model import Model


class StackedInline(BaseStackedInline):
    """Inline admin with fields stacked vertically."""

    formfield_overrides = FORM_FIELD_OVERRIDES


class TabularInline(BaseTabularInline):
    """Inline admin with fields laid out horizontally."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    def get_extra(
        self,
        request: 'HttpRequest',
        obj: Optional['Model'] = None,
        **kwargs,
    ) -> int:
        """Return the number of extra/blank rows to display."""
        if obj:
            if self.fk_name:
                fk_name = self.fk_name
            elif hasattr(self.model, 'content_object'):
                fk_name = 'content_object'
            elif obj._meta.proxy and obj._meta.proxy_for_model:
                fk_name = obj._meta.proxy_for_model.__name__.lower()
            elif getattr(obj, 'polymorphic_ctype_id', None):
                fk_name = list(obj.__class__._meta.parents.keys())[0].__name__.lower()
            elif obj._meta.model_name:
                fk_name = obj._meta.model_name
            else:
                raise Exception('Unable to determine foreign key field name.')
            try:
                if len(self.get_queryset(request).filter(**{f'{fk_name}_id': obj.pk})):
                    return 0
            except (FieldError, FieldDoesNotExist) as err:
                logging.error(err)
        return 1
