from typing import List

from nested_admin.nested import (
    NestedGenericStackedInline,
    NestedGenericTabularInline,
    NestedStackedInline,
    NestedTabularInline,
)

from admin.model_admin import FORM_FIELD_OVERRIDES

# GenericTabularInline = NestedGenericTabularInline
# GenericStackedInline = NestedGenericStackedInline


class GenericTabularInline(NestedGenericTabularInline):
    """Tabular inline admin for generically related objects."""

    formfield_overrides = FORM_FIELD_OVERRIDES


class GenericStackedInline(NestedGenericStackedInline):
    """Stacked inline admin for generically related objects."""

    formfield_overrides = FORM_FIELD_OVERRIDES


class StackedInline(NestedStackedInline):
    """Inline admin with fields stacked vertically."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    def get_fields(self, request, model_instance=None) -> List[str]:
        """Return reordered fields to be displayed in the admin."""
        fields = super().get_fields(request, model_instance)
        return reorder_fields(fields)


class TabularInline(NestedTabularInline):
    """Inline admin with fields laid out horizontally."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    def get_fields(self, request, model_instance=None) -> List[str]:
        """Return reordered fields to be displayed in the admin."""
        fields = super().get_fields(request, model_instance)
        return reorder_fields(fields)


def reorder_fields(fields) -> List[str]:
    """Return a reordered list of fields to display in the admin."""
    ordered_fields = ('page_number', 'end_page_number', 'notes', 'position')
    for field_name in ordered_fields:
        if field_name in fields:
            fields.remove(field_name)
            fields.append(field_name)
    return fields
