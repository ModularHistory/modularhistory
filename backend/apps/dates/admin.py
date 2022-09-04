from typing import TYPE_CHECKING

from apps.admin.model_admin import ExtendedModelAdmin

if TYPE_CHECKING:
    from apps.dates.models import DatedModel


class DatedModelAdmin(ExtendedModelAdmin):
    """Model admin for searchable models."""

    model: type['DatedModel']
