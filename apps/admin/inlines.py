from typing import Optional, TYPE_CHECKING

# from django.contrib.admin import StackedInline as BaseStackedInline
# from django.contrib.admin import TabularInline as BaseTabularInline
from nested_admin.nested import NestedStackedInline, NestedTabularInline

from apps.admin.model_admin import FORM_FIELD_OVERRIDES

if TYPE_CHECKING:
    from core.models.model import Model


class StackedInline(NestedStackedInline):
    """Inline admin with fields stacked vertically."""

    formfield_overrides = FORM_FIELD_OVERRIDES


class TabularInline(NestedTabularInline):
    """Inline admin with fields laid out horizontally."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    def get_extra(self, request, model_instance: Optional['Model'] = None, **kwargs):
        """Return the number of extra/blank rows to display."""
        if len(self.get_queryset(request)):
            return 0
        return 1
