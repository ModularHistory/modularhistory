from typing import TYPE_CHECKING, Optional

from django.contrib.admin import StackedInline as BaseStackedInline
from django.contrib.admin import TabularInline as BaseTabularInline

from apps.admin.model_admin import FORM_FIELD_OVERRIDES

if TYPE_CHECKING:
    from core.models.model import Model


class StackedInline(BaseStackedInline):
    """Inline admin with fields stacked vertically."""

    formfield_overrides = FORM_FIELD_OVERRIDES


class TabularInline(BaseTabularInline):
    """Inline admin with fields laid out horizontally."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    def get_extra(self, request, obj: Optional['Model'] = None, **kwargs):
        """Return the number of extra/blank rows to display."""
        if obj:
            if self.fk_name:
                fk_name = self.fk_name
            elif hasattr(self.model, 'content_object'):
                fk_name = 'content_object'
            else:
                fk_name = obj.__class__.__name__.lower()
            if len(self.get_queryset(request).filter(**{f'{fk_name}_id': obj.id})):
                return 0
        return 1
