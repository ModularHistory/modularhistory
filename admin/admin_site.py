from typing import TYPE_CHECKING, Dict, Type

from django.contrib.admin import AdminSite as BaseAdminSite
from massadmin.massadmin import mass_change_selected

if TYPE_CHECKING:
    from admin.model_admin import ModelAdmin
    from modularhistory.models import Model


class AdminSite(BaseAdminSite):
    """ModularHistory's admin site."""

    site_header = 'ModularHistory administration'

    def get_registry(self) -> Dict[Type['Model'], 'ModelAdmin']:
        """Return a dict of Model -> ModelAdmin."""
        return self._registry


admin_site = AdminSite(name='admin')
admin_site.add_action(mass_change_selected)
