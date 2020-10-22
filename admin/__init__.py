"""Admin app for ModularHistory."""

from .inlines import (
    GenericStackedInline,
    GenericTabularInline,
    StackedInline,
    TabularInline,
)
from .model_admin import ModelAdmin, admin_site
from .searchable_model_admin import SearchableModelAdmin
