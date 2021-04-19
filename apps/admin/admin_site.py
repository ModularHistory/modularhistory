from django.contrib.admin import AdminSite as BaseAdminSite
from massadmin.massadmin import mass_change_selected


class AdminSite(BaseAdminSite):
    """ModularHistory's admin site."""

    site_header = 'ModularHistory administration'

    def get_registry(self):
        """Return a dict of Model -> ModelAdmin."""
        return self._registry


admin_site = AdminSite(name='admin')
admin_site.add_action(mass_change_selected)
