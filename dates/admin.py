from typing import TYPE_CHECKING, Type

from admin.model_admin import ModelAdmin, admin_site
from dates import models
from entities.views import EntityCategorySearchView, EntitySearchView
from topics.views import TagSearchView

if TYPE_CHECKING:
    from dates.models import DatedModel


class DatedModelAdmin(ModelAdmin):
    """Model admin for searchable models."""

    model: Type['DatedModel']

    exclude = ['computations']
    readonly_fields = ['pretty_computations']
