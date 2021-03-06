from typing import TYPE_CHECKING, Type

from admin.model_admin import ModelAdmin

if TYPE_CHECKING:
    from apps.dates.models import DatedModel


class DatedModelAdmin(ModelAdmin):
    """Model admin for searchable models."""

    model: Type['DatedModel']

    exclude = ['computations']
    readonly_fields = ['pretty_computations']
