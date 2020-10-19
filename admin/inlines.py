from typing import List

from nested_admin.nested import (
    NestedGenericStackedInline,
    NestedGenericTabularInline,
    NestedStackedInline,
    NestedTabularInline
)

from admin.model_admin import FORM_FIELD_OVERRIDES

GenericTabularInline = NestedGenericTabularInline
GenericStackedInline = NestedGenericStackedInline


class StackedInline(NestedStackedInline):
    """TODO: add docstring."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    def get_fields(self, request, model_instance=None) -> List[str]:
        """TODO: add docstring."""
        fields = super().get_fields(request, model_instance)
        return reorder_fields(fields)


class TabularInline(NestedTabularInline):
    """TODO: add docstring."""

    formfield_overrides = FORM_FIELD_OVERRIDES

    def get_fields(self, request, model_instance=None) -> List[str]:
        """TODO: add docstring."""
        fields = super().get_fields(request, model_instance)
        return reorder_fields(fields)


def reorder_fields(fields) -> List[str]:
    """TODO: add docstring."""
    ordered_fields = (
        'page_number',
        'end_page_number',
        'notes',
        'position'
    )
    for field_name in ordered_fields:
        if field_name in fields:
            fields.remove(field_name)
            fields.append(field_name)
    return fields
